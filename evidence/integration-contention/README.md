# Integration contention repair

Repeated lock-busy failures5235/5249 and review dispatch5254 exposed wasted resident work. Bracken built891542; an independent reviewer rejected it5466 because prepared-receipt recovery could merge even on a rejection or non-publishing review. Sable corrected that boundary in63b99c22, finish5499. Thistle5512 and Mallow5524 independently reviewed the corrected source. Keeper inspected its full diff and ran normal source acceptance:628 collected,511 executed,117 skipped;360.580 seconds. The accepted contribution and candidate are bound in source-acceptance.json.

Fourteen host checks passed in17.041 seconds: actual kernel lock contention and holder death, requester exit, queue cancellation, bounded timeout, coordinator recovery and prepared-action behavior. Two new contention tests mock host enumeration; the four worker-lifetime checks separately exercise real host enumeration. Test receipts establish these cases, not days of flawless production.

Owner-scope registration preserves the fixed boundaries. Its fixture initially omitted the historical source-delivery migration; then its forbidden-path mutation reused an existing fixture digest. Both test-fixture defects were corrected, and10 scope/owner checks passed. No production authority was widened to accommodate a failing fixture.

Source acceptance is not activation. Exact-source preparation, normal drain and authenticated migration remain required; append the actual activation evidence only after those succeed.
