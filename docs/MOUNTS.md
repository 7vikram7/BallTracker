# Camera mounts: what moved in field test 5, and a mount that fits any bar

Field test 5 (2026-11-25, session `20261125-194731`, decision log entry 34): the phones were clamped
to the hall's steel frame. Measured from the recorded snapshots (`scripts/camera_motion.py`, every
snapshot registered against the frame of the last hand calibration, players masked out by
requiring 150+ background matches):

| camera | how it moved | after 5 / 10 / 20 min | worst | what it did to bounce positions |
|---|---|---|---|---|
| Samsung | **tilted down slowly, then dropped**: 4° of tilt in 27 min, 73 px of it in one step at minute 27 | 5 / 7 / 17 px | 99 px | 1.5-2.7 m off the iPhone 17 after the drop, for the rest of the session |
| iPhone 15 Pro | **turned sideways in steps** (pan): 45 px, then 200 px, then 238 px, ending 8° off | (steps) | 240 px | 2.2-2.3 m off the iPhone 17 for 35 minutes |
| iPhone 17 | small changes, all followed automatically (13 corrections) | 0 / 5 / 5 px | 14 px | none (followed) |

At 1080p one degree is about 23 px, and at the far baseline one degree of tilt moves a bounce by
1-3 m. The drift check follows changes of 3-80 px (and now bigger ones the court lines confirm),
so a mount doesn't need to be perfect. It needs to **not sag and not turn when touched**.

The two failures have different causes:

* **Sag (the Samsung):** the phone's weight sits in front of a friction joint (a small ball
  head or the holder's hinge). The joint gives way a little at a time, then all at once. It moves
  in tilt, the direction gravity pulls.
* **Turning (the iPhone 15 Pro):** a bump, a cable tug or a player brushing past turns the clamp
  around a round bar, or turns the phone inside a spring holder. It moves in pan, around the bar.

## What makes a mount steady

1. **A clamp that can't turn on the bar.** It needs two lines of contact (a V, or two jaws),
   rubber-lined, and screw-tightened, not spring-loaded. On a round bar, use two straps or clamps
   about 10 cm apart, not one: a single strap is a pivot.
2. **A short chain: clamp → head → phone.** Every extra joint is a hinge. No magic arms, goosenecks,
   flexible tripod legs or extension rods.
3. **A head that can't sag.** Use a ball head with a ball of 30 mm or more, or a pan-tilt head with
   a separate lock for each axis. Put the phone's centre over the head, not out in front. After
   aiming, add a zip tie or strap across the joint as a second lock.
4. **A phone holder that grips by screw**, or a phone case/cage with a 1/4" thread. Spring holders
   let the phone rotate when it's tapped.
5. **Up and out of the way**: 2.2-3 m high on a **vertical structural post** at a corner. Not on
   the netting rails or the net itself, which sway when a ball hits them. Not where players swing.
   The Samsung was low enough that a player's head and paddle filled its view.
6. **Cables tied to the post**, with a loop of slack, so a pull on the power bank cable doesn't
   twist the phone.
7. **A safety tether**: a lanyard from the phone or holder to the post.

## The mount: two kits that cover any bar

**Kit A: bars 13-55 mm (round, square or flat; vertical or horizontal).** Quick to put on.

* A super clamp: Manfrotto 035 (13-55 mm, rated 15 kg), or the cheaper SmallRig 735 type
  (15-44 mm), with a 1/4" or 3/8" stud.
* A ball head with a 30 mm+ ball and a separate pan lock, screwed directly onto the stud.
* A metal phone clamp with a tightening screw.

**Kit B: posts and pillars 40-150 mm (round or square), any orientation.** Steadiest; about the
price of a meal from a hardware shop.

* A V-block: a 120 mm piece of aluminium angle (40 × 40 × 4 mm), with a slot near each end. The
  V centres itself on any round post and sits flat on a square one.
* Two stainless steel worm-drive hose clamps (sized for the post, e.g. 60-100 mm) or two small
  ratchet straps through the slots, 10 cm apart. A strip of bicycle inner tube under the V for
  grip.
* A 1/4"-20 bolt through the middle of the angle (lock nut behind) into the same ball head and
  phone clamp as kit A.

Both kits use the same head and phone clamp, so a camera can move between a thin rail and a thick
post.

## Every session

1. Mark each mount's spot on its post with tape (height and direction) and put it back on the
   mark. The previous calibration then snaps to the lines by itself at the start.
2. **Wiggle test:** after aiming, push the phone gently sideways and down, and let go. The
   dashboard's drift reading should come back to under 3 px. If it doesn't, tighten the joint.
3. Battery packs, cables tied down (the Samsung started at 28% and died at minute 47).

## What the server now does when a camera moves anyway

* Small moves (3-80 px): followed automatically, as before.
* Bigger moves: followed if the background matches well and the painted lines confirm the new
  position. On the field-test-5 recording this worked for the iPhone 15 Pro's 146 px turn; its
  300 px turn was confirmed in one replay setup and not in another, so don't count on it.
* A move it can't follow: the camera is **taken out of the calls** until it's recalibrated or
  put back (before, it kept calling with the wrong calibration, 2.4 m off), and the dashboard
  says so. Recalibrate it then.
* A calibration saved in an earlier session is used only once the court lines confirm it (the
  iPhone 17 called for 15 minutes on one that put it at the other end of the court).
