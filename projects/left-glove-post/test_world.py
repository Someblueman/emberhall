"""Run the shipped chart model; page interaction is tried in the native viewer."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node runs the browser model")
class WorldTests(unittest.TestCase):
    def check_js(self, checks):
        model = Path(__file__).with_name("world.js")
        result = subprocess.run(
            ["node", "-e", "const assert=require('node:assert/strict');"
             "const W=require(process.argv[1]);" + checks, str(model)],
            text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_loop_transport_and_delivery(self):
        self.check_js("""
const circuit=(s,d)=>Array.from({length:5}).reduce(s=>W.move(s,d),s);
const original=W.start();
assert(W.atCounter(original));assert(!W.fits(original));
assert.equal(W.deliver(original),original);
const ordinary=circuit(original,'north');
assert(W.atCounter(ordinary));assert(!W.fits(ordinary));
const once=circuit(original,'east');
assert(W.atCounter(once));assert(W.fits(once));assert.equal(once.steps,5);
const twice=circuit(once,'east');
assert(W.atCounter(twice));assert(!W.fits(twice));assert.equal(twice.steps,10);
const delivered=W.deliver(once);assert(delivered.delivered);
assert.equal(W.move(delivered,'north'),delivered);
const away=W.move(once,'north');assert(W.fits(away));
assert(!W.atCounter(away));assert.equal(W.deliver(away),away);
assert.deepEqual(original,W.start()); // moves never mutate the origin
""")

    def test_every_chart_point_inverse_steps_and_twist(self):
        self.check_js("""
for(let x=0;x<W.size;x++)for(let y=0;y<W.size;y++)for(const turned of [false,true]){
 const s={...W.start(),x,y,turned};
 for(const [a,b]of [['east','west'],['west','east'],['north','south'],['south','north']]){
  const back=W.move(W.move(s,a),b);
  assert.deepEqual([back.x,back.y,back.turned],[x,y,turned]);
 }
 const across=Array.from({length:W.size}).reduce(s=>W.move(s,'east'),s);
 assert.deepEqual([across.x,across.y,across.turned],[x,4-y,!turned]);
 const ordinary=Array.from({length:W.size}).reduce(s=>W.move(s,'south'),s);
 assert.deepEqual([ordinary.x,ordinary.y,ordinary.turned],[x,y,turned]);
}
assert.throws(()=>W.move(W.start(),'__proto__'),RangeError);
assert.throws(()=>W.move(W.start(),'teleport'),RangeError);
""")


if __name__ == "__main__":
    unittest.main()
