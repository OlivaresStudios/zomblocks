/* 3D viewer of the add-on's Bedrock models (classic script: works from file:// too).
 * Geometry maths = geo_render.py / Blockbench: x negated, rotations (-rx, -ry, rz) applied Z*Y*X, box UV.
 * Animations: keyframes or Molang (degrees); queries the wiki cannot know (variables, properties...) read 0. */
(function () {
	"use strict";
	var THREE = window.THREE;
	var D2R = Math.PI / 180;

	// ------------------------------------------------------------------ Molang
	var CACHE = {};
	var QUERY_TIME = /\b(query|q)\.(anim_time|life_time|time_stamp)\b/g;
	function compile(expr) {
		if (CACHE[expr]) return CACHE[expr];
		var e = String(expr).toLowerCase();
		if (e.indexOf("return") >= 0 || e.indexOf(";") >= 0) e = e.replace(/^.*return\s+/, "").replace(/;\s*$/, "");
		e = e.replace(QUERY_TIME, "__t")
			.replace(/\b(query|q)\.(modified_distance_moved|walk_distance)\b/g, "(__t*4)")
			.replace(/\b(query|q)\.(modified_move_speed|ground_speed|is_moving|is_on_ground|is_alive)\b/g, "1")
			.replace(/\b(query|q)\.\w+\s*\([^()]*\)/g, "0")
			.replace(/\b(query|q|variable|v|temp|t|context|c)\.\w+/g, "0")
			.replace(/math\.(sin|cos)\(/g, "M_$1(")
			.replace(/math\.(asin|acos|atan|atan2)\(/g, "M_$1(")
			.replace(/math\.(abs|sqrt|pow|floor|ceil|round|trunc|exp|min|max)\(/g, "Math.$1(")
			.replace(/math\.ln\(/g, "Math.log(")
			.replace(/math\.(mod|clamp|lerp|lerprotate|random|random_integer|die_roll|hermite_blend)\(/g, "M_$1(")
			.replace(/math\.pi/g, "Math.PI");
		var fn;
		try { fn = new Function("__t", "M_sin", "M_cos", "M_asin", "M_acos", "M_atan", "M_atan2", "M_mod", "M_clamp", "M_lerp", "M_lerprotate", "M_random", "M_random_integer", "M_die_roll", "M_hermite_blend", "return (" + e + ");"); }
		catch (err) { fn = function () { return 0; }; }
		CACHE[expr] = fn;
		return fn;
	}
	var F = [
		function (x) { return Math.sin(x * D2R); }, function (x) { return Math.cos(x * D2R); },
		function (x) { return Math.asin(x) / D2R; }, function (x) { return Math.acos(x) / D2R; },
		function (x) { return Math.atan(x) / D2R; }, function (y, x) { return Math.atan2(y, x) / D2R; },
		function (a, b) { return a % b; }, function (v, lo, hi) { return Math.max(lo, Math.min(hi, v)); },
		function (a, b, k) { return a + (b - a) * k; }, function (a, b, k) { return a + (b - a) * k; },
		function (a, b) { return a; }, function (a) { return a; }, function (n, s) { return n; },
		function (k) { return 3 * k * k - 2 * k * k * k; }
	];
	function molang(value, t) {
		if (typeof value === "number") return value;
		if (typeof value === "boolean") return value ? 1 : 0;
		var v;
		try { v = compile(value).apply(null, [t].concat(F)); } catch (err) { v = 0; }
		return isFinite(v) ? Number(v) : 0;
	}
	function vec(v, t) {
		if (Array.isArray(v)) return [molang(v[0], t), molang(v[1], t), molang(v[2], t)];
		var s = molang(v, t);
		return [s, s, s];
	}
	function frame(f, t) {
		if (f && typeof f === "object" && !Array.isArray(f)) return vec(f.post || f.pre || [0, 0, 0], t);
		return vec(f, t);
	}
	function sample(channel, t) {
		if (channel == null) return null;
		if (Array.isArray(channel) || typeof channel !== "object") return vec(channel, t);
		var keys = Object.keys(channel).map(Number).sort(function (a, b) { return a - b; });
		if (!keys.length) return null;
		if (t <= keys[0]) return frame(channel[String(keys[0])] || channel[keys[0].toFixed(2)] || channel[Object.keys(channel)[0]], t);
		var lookup = {};
		Object.keys(channel).forEach(function (k) { lookup[Number(k)] = channel[k]; });
		if (t >= keys[keys.length - 1]) return frame(lookup[keys[keys.length - 1]], t);
		var i = 0;
		while (i < keys.length - 1 && keys[i + 1] < t) i++;
		var a = frame(lookup[keys[i]], t), b = frame(lookup[keys[i + 1]], t), k = (t - keys[i]) / (keys[i + 1] - keys[i]);
		return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
	}

	// ------------------------------------------------------------------ geometry
	function bb(p) { return [-p[0], p[1], p[2]]; }
	function rot(rx, ry, rz) {
		var m = new THREE.Matrix4().makeRotationZ(rz * D2R);
		m.multiply(new THREE.Matrix4().makeRotationY(-ry * D2R));
		m.multiply(new THREE.Matrix4().makeRotationX(-rx * D2R));
		return m;
	}
	function aroundPivot(piv, R) {
		var T = new THREE.Matrix4().makeTranslation(piv[0], piv[1], piv[2]);
		var Ti = new THREE.Matrix4().makeTranslation(-piv[0], -piv[1], -piv[2]);
		return T.multiply(R).multiply(Ti);
	}
	function boneMatrix(bone, pose) {
		var r = (bone.rotation || [0, 0, 0]).slice();
		if (pose && pose.rotation) { r[0] += pose.rotation[0]; r[1] += pose.rotation[1]; r[2] += pose.rotation[2]; }
		var piv = bb(bone.pivot || [0, 0, 0]);
		var M = aroundPivot(piv, rot(r[0], r[1], r[2]));
		if (pose && pose.scale) M.multiply(aroundPivot(piv, new THREE.Matrix4().makeScale(pose.scale[0], pose.scale[1], pose.scale[2])));
		if (pose && pose.position) { var p = bb(pose.position); M.premultiply(new THREE.Matrix4().makeTranslation(p[0], p[1], p[2])); }
		return M;
	}
	function corners(x0, y0, z0, x1, y1, z1) {
		return {
			north: [[x1, y1, z0], [x0, y1, z0], [x1, y0, z0], [x0, y0, z0]],
			south: [[x0, y1, z1], [x1, y1, z1], [x0, y0, z1], [x1, y0, z1]],
			east: [[x1, y1, z1], [x1, y1, z0], [x1, y0, z1], [x1, y0, z0]],
			west: [[x0, y1, z0], [x0, y1, z1], [x0, y0, z0], [x0, y0, z1]],
			up: [[x1, y1, z1], [x0, y1, z1], [x1, y1, z0], [x0, y1, z0]],
			down: [[x1, y0, z1], [x0, y0, z1], [x1, y0, z0], [x0, y0, z0]]
		};
	}
	function boxUV(s, uv, mirror) {
		var w = s[0], h = s[1], d = s[2], u = uv[0], v = uv[1];
		var f = {
			east: [u, v + d, u + d, v + d + h], north: [u + d, v + d, u + d + w, v + d + h],
			west: [u + d + w, v + d, u + 2 * d + w, v + d + h], south: [u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h],
			up: [u + d, v, u + d + w, v + d], down: [u + d + w, v, u + d + 2 * w, v + d]
		};
		if (mirror) {
			var e = f.east; f.east = f.west; f.west = e;
			Object.keys(f).forEach(function (k) { f[k] = [f[k][2], f[k][1], f[k][0], f[k][3]]; });
		}
		return f;
	}
	function cubeGeometry(cube, boneMirror, tw, th) {
		var o = cube.origin, s = cube.size, inf = cube.inflate || 0;
		var mirror = cube.mirror != null ? cube.mirror : boneMirror;
		var x0 = -(o[0] + s[0]) - inf, x1 = -o[0] + inf, y0 = o[1] - inf, y1 = o[1] + s[1] + inf, z0 = o[2] - inf, z1 = o[2] + s[2] + inf;
		var uvs = {};
		if (Array.isArray(cube.uv)) uvs = boxUV(s, cube.uv, mirror);
		else Object.keys(cube.uv || {}).forEach(function (k) { var a = cube.uv[k]; uvs[k] = [a.uv[0], a.uv[1], a.uv[0] + a.uv_size[0], a.uv[1] + a.uv_size[1]]; });
		var c = corners(x0, y0, z0, x1, y1, z1), pos = [], uv = [];
		Object.keys(c).forEach(function (face) {
			if (!uvs[face]) return;
			var q = c[face], r = uvs[face];
			var A = [r[0] / tw, 1 - r[1] / th], B = [r[2] / tw, 1 - r[1] / th], C = [r[0] / tw, 1 - r[3] / th], E = [r[2] / tw, 1 - r[3] / th];
			pos.push.apply(pos, q[0].concat(q[2], q[1], q[1], q[2], q[3]));
			uv.push.apply(uv, A.concat(C, B, B, C, E));
		});
		var g = new THREE.BufferGeometry();
		g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
		g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
		g.computeVertexNormals();
		return g;
	}
	function buildModel(geo, texture) {
		var g = geo["minecraft:geometry"][0], d = g.description || {};
		var tw = d.texture_width || 64, th = d.texture_height || 64;
		var material = new THREE.MeshLambertMaterial({ map: texture, side: THREE.DoubleSide, alphaTest: 0.5 });
		var root = new THREE.Group(), bones = {};
		g.bones.forEach(function (b) { var grp = new THREE.Group(); grp.matrixAutoUpdate = false; bones[b.name] = { bone: b, group: grp }; });
		g.bones.forEach(function (b) {
			var entry = bones[b.name], parent = b.parent && bones[b.parent];
			(parent ? parent.group : root).add(entry.group);
			if (b.name.indexOf("glow_") === 0) return;
			(b.cubes || []).forEach(function (cube) {
				var mesh = new THREE.Mesh(cubeGeometry(cube, b.mirror, tw, th), material);
				if (cube.rotation) {
					var sub = new THREE.Group(); sub.matrixAutoUpdate = false;
					sub.matrix.copy(aroundPivot(bb(cube.pivot || [0, 0, 0]), rot(cube.rotation[0], cube.rotation[1], cube.rotation[2])));
					sub.add(mesh); entry.group.add(sub);
				} else entry.group.add(mesh);
			});
		});
		return { root: root, bones: bones, material: material };
	}
	function pose(model, clip, t) {
		var channels = (clip && clip.bones) || {};
		Object.keys(model.bones).forEach(function (name) {
			var entry = model.bones[name], ch = channels[name], p = null;
			if (ch) p = { rotation: sample(ch.rotation, t), position: sample(ch.position, t), scale: sample(ch.scale, t) };
			entry.group.matrix.copy(boneMatrix(entry.bone, p));
		});
		model.root.updateMatrixWorld(true);
	}
	function clipTime(clip, t) {
		var len = clip.animation_length || 2;
		if (clip.loop === true || clip.loop === "true") return t % len;
		if (clip.loop === "hold_on_last_frame") return Math.min(t, len);
		return t % (len + 1.2) > len ? len : t % (len + 1.2);           // one shot: plays, holds a moment, starts again
	}
	function texture(uri) {
		var t = new THREE.TextureLoader().load(uri);
		t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace;
		return t;
	}

	// ------------------------------------------------------------------ viewer
	function Viewer(el, bundle, still) {
		var self = this;
		this.el = el; this.bundle = bundle; this.t = 0; this.zoom = (bundle.view && bundle.view.zoom) || 1;
		this.yaw = bundle.view ? bundle.view.yaw : -0.5; this.pitch = bundle.view ? bundle.view.pitch : 0.18;
		this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
		this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
		this.renderer.setClearColor(0x000000, 0);
		el.appendChild(this.renderer.domElement);
		this.scene = new THREE.Scene();
		this.scene.add(new THREE.HemisphereLight(0xffffff, 0x445544, 2.4));
		var sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(-0.6, 1.4, -1); this.scene.add(sun);
		this.camera = new THREE.PerspectiveCamera(30, 1, 0.1, 5000);
		this.textures = bundle.textures.map(texture);
		this.model = buildModel(bundle.geo, this.textures[0]);
		this.scene.add(this.model.root);
		pose(this.model, null, 0);
		// extra models drawn with it (armor pieces worn by a survivor): same bone names, same animations
		this.layers = (bundle.layers || []).map(function (l) {
			var m = buildModel(l.geo, texture(l.texture));
			if (l.additive) {                                  // holograms: black = nothing, colours add up
				m.material.transparent = true; m.material.alphaTest = 0; m.material.depthWrite = false;
				m.material.blending = THREE.AdditiveBlending;
			}
			if (l.offset) m.root.position.set(-l.offset[0], l.offset[1], l.offset[2]);
			m.clip = l.anim || null;
			self.scene.add(m.root);
			pose(m, m.clip, 0);
			return m;
		});
		var box = new THREE.Box3().setFromObject(this.model.root);
		this.layers.forEach(function (m) { box.union(new THREE.Box3().setFromObject(m.root)); });
		var size = box.getSize(new THREE.Vector3());
		this.center = box.getCenter(new THREE.Vector3());
		this.radius = Math.max(size.x, size.y * 1.05, size.z) * 0.8;
		var shadow = new THREE.Mesh(new THREE.CircleGeometry(Math.max(size.x, size.z) * 0.75, 40), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 }));
		shadow.rotation.x = -Math.PI / 2; shadow.position.set(this.center.x, box.min.y + 0.05, this.center.z); this.scene.add(shadow);
		this.setAnim(Object.keys(bundle.anims)[0]);
		this.setMod("");
		this.clock = new THREE.Clock();
		(function loop() { if (self.dead) return; requestAnimationFrame(loop); self.frame(); })();
		el.classList.add("live");
		if (still) return;
		// drag to turn, wheel to zoom
		var drag = null;
		el.addEventListener("pointerdown", function (e) { drag = { x: e.clientX, y: e.clientY }; el.setPointerCapture(e.pointerId); el.style.cursor = "grabbing"; });
		el.addEventListener("pointermove", function (e) {
			if (!drag) return;
			self.yaw -= (e.clientX - drag.x) * 0.01; self.pitch = Math.max(-0.2, Math.min(1.2, self.pitch + (e.clientY - drag.y) * 0.008));
			drag = { x: e.clientX, y: e.clientY };
		});
		el.addEventListener("pointerup", function () { drag = null; el.style.cursor = ""; });
		el.addEventListener("wheel", function (e) { e.preventDefault(); self.zoom = Math.max(0.5, Math.min(2.2, self.zoom * (e.deltaY > 0 ? 1.08 : 0.92))); }, { passive: false });
	}
	Viewer.prototype.dispose = function () {
		this.dead = true;
		this.renderer.dispose();
		if (this.renderer.forceContextLoss) this.renderer.forceContextLoss();
		if (this.renderer.domElement.parentNode) this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
	};
	/** play an animation once and hold its last frame */
	Viewer.prototype.playOnce = function (key) {
		var clip = this.bundle.anims[key];
		this.steps = [{ key: key, dur: 1e9, once: true }];
		this.step = 0; this.stepT = 0;
		this.setAnim(key);
		return clip ? (clip.animation_length || 2) : 0;
	};
	Viewer.prototype.setAnim = function (key) { this.clip = this.bundle.anims[key] || null; this.t = 0; };
	Viewer.prototype.setSkin = function (i) { if (this.textures[i]) this.model.material.map = this.textures[i]; };
	/** weapon mods: the decorations are hidden bones mod_<letter>... ("" = no mod) */
	Viewer.prototype.setMod = function (letter) {
		var bones = this.model.bones;
		Object.keys(bones).forEach(function (name) {
			if (name.indexOf("mod_") === 0) bones[name].group.visible = !!letter && name.indexOf("mod_" + letter) === 0;
		});
	};
	/** zombie pages: walk for a few strides, then the death, held a moment, and again */
	Viewer.prototype.cycle = function () {
		var anims = this.bundle.anims, keys = Object.keys(anims);
		var death = keys.filter(function (k) { return k.indexOf("death") === 0; }).sort()[0];
		var walk = anims.walk ? "walk" : keys.filter(function (k) { return k !== death; })[0];
		this.steps = [];
		if (walk) { var wl = anims[walk].animation_length || 1; this.steps.push({ key: walk, dur: Math.max(3, wl * Math.ceil(3 / wl)) }); }
		if (death) this.steps.push({ key: death, dur: (anims[death].animation_length || 2) + 1.2, once: true });
		this.step = 0; this.stepT = 0;
		if (this.steps.length) this.setAnim(this.steps[0].key);
	};
	Viewer.prototype.frame = function () {
		var dt = Math.min(0.1, this.clock.getDelta());
		this.t += dt;
		if (this.steps && this.steps.length) {
			this.stepT += dt;
			var st = this.steps[this.step];
			if (this.stepT >= st.dur) { this.step = (this.step + 1) % this.steps.length; this.stepT = 0; this.setAnim(this.steps[this.step].key); st = this.steps[this.step]; }
			if (st.once) this.t = Math.min(this.stepT, this.clip ? (this.clip.animation_length || 2) : 0);
		}
		if (this.clip) {
			var ct = clipTime(this.clip, this.t), clip = this.clip;
			pose(this.model, clip, ct);
			this.layers.forEach(function (m) { if (!m.clip) pose(m, clip, ct); });
		}
		var t = this.t;
		this.layers.forEach(function (m) { if (m.clip) pose(m, m.clip, clipTime(m.clip, t)); });
		var w = this.el.clientWidth || 1, h = this.el.clientHeight || 1;
		if (this._w !== w || this._h !== h) { this.renderer.setSize(w, h, false); this.camera.aspect = w / h; this.camera.updateProjectionMatrix(); this._w = w; this._h = h; }
		var dist = this.radius / Math.tan(this.camera.fov * D2R / 2) * this.zoom;
		var c = this.center;
		this.camera.position.set(c.x + Math.sin(this.yaw) * Math.cos(this.pitch) * dist, c.y + Math.sin(this.pitch) * dist, c.z - Math.cos(this.yaw) * Math.cos(this.pitch) * dist);
		this.camera.lookAt(c);
		this.renderer.render(this.scene, this.camera);
	};

	// ------------------------------------------------------------------ page wiring
	// zombie list: hovering a card (holding it on a phone) plays the death once in 3D, then the picture comes back
	var loaded = {};
	function loadModel(src, id, done) {
		if (window.WIKI_MODELS && window.WIKI_MODELS[id]) return done();
		if (loaded[id]) { loaded[id].push(done); return; }
		loaded[id] = [done];
		var s = document.createElement("script");
		s.src = src;
		s.onload = function () { var list = loaded[id]; loaded[id] = null; list.forEach(function (f) { f(); }); };
		document.head.appendChild(s);
	}
	function deathPreview(card, root) {
		var id = card.getAttribute("data-model"), pic = card.querySelector(".pic"), img = pic && pic.querySelector("img");
		if (!id || !pic || card._preview) return;
		card._preview = { pending: true };
		loadModel(root + "models/" + id + ".js", id, function () {
			var state = card._preview;
			if (!state || !state.pending) return;
			var bundle = window.WIKI_MODELS[id];
			var death = bundle && Object.keys(bundle.anims).filter(function (k) { return k.indexOf("death") === 0; }).sort()[0];
			if (!death || !window.THREE) { card._preview = null; return; }
			var box = document.createElement("div");
			box.className = "preview3d";
			pic.appendChild(box);
			var v;
			try { v = new Viewer(box, bundle, true); } catch (err) { box.remove(); card._preview = null; return; }
			v.zoom = 0.62;                                   // framed like the picture of the card
			var len = v.playOnce(death);
			if (img) img.style.visibility = "hidden";
			state.pending = false; state.viewer = v; state.box = box;
			state.timer = setTimeout(function () { stopPreview(card); }, (len + 0.6) * 1000);
		});
	}
	function stopPreview(card) {
		var state = card._preview;
		card._preview = null;
		if (!state) return;
		state.pending = false;
		clearTimeout(state.timer);
		if (state.viewer) state.viewer.dispose();
		if (state.box) state.box.remove();
		var img = card.querySelector(".pic img");
		if (img) img.style.visibility = "";
	}

	window.WikiViewer = {
		hoverDeath: function (root) {
			document.querySelectorAll(".card[data-model]").forEach(function (card) {
				var hold = null;
				card.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") deathPreview(card, root); });
				card.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") stopPreview(card); });
				card.addEventListener("pointerdown", function (e) {
					if (e.pointerType === "mouse") return;
					hold = setTimeout(function () { hold = null; card._held = true; deathPreview(card, root); }, 250);
				});
				["pointerup", "pointercancel"].forEach(function (ev) { card.addEventListener(ev, function () { if (hold) clearTimeout(hold); hold = null; }); });
				card.addEventListener("contextmenu", function (e) { if (card._held) e.preventDefault(); });
				card.addEventListener("click", function (e) { if (card._held) { e.preventDefault(); card._held = false; } });
			});
		},
		mount: function (id, options) {
			var el = document.getElementById("viewer");
			var bundle = window.WIKI_MODELS && window.WIKI_MODELS[id];
			if (!el || !bundle || !THREE) return;
			var v;
			try { v = new Viewer(el, bundle); } catch (err) { return; }
			if (options && options.cycle) v.cycle();
			document.querySelectorAll("[data-anim]").forEach(function (b) {
				b.addEventListener("click", function () {
					document.querySelectorAll("[data-anim]").forEach(function (o) { o.classList.toggle("on", o === b); });
					v.setAnim(b.getAttribute("data-anim"));
				});
			});
			document.querySelectorAll("[data-mod]").forEach(function (b) {
				b.addEventListener("click", function () {
					document.querySelectorAll("[data-mod]").forEach(function (o) { o.classList.toggle("on", o === b); });
					v.setMod(b.getAttribute("data-mod"));
				});
			});
			document.querySelectorAll("[data-skin]").forEach(function (f) {
				f.addEventListener("click", function () {
					document.querySelectorAll("[data-skin]").forEach(function (o) { o.classList.toggle("on", o === f); });
					v.setSkin(Number(f.getAttribute("data-skin")));
					el.scrollIntoView({ behavior: "smooth", block: "center" });
				});
			});
		}
	};
})();
