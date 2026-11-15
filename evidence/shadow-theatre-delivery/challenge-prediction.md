# Single Gate pre-adjustment prediction

Recorded 2026-11-15 approximately 06:53 UTC, after selecting the public
Single Gate challenge but before changing its light or prop controls.
No stored solution or application source has been inspected.

The visible UI gives target [25, 75], light (0, 50), and selected prop at
x=50, yLow=40, yHigh=60. It currently displays interval [30, 70], length40.
The stage depicts a vertical screen to the right; the preceding known
geometry used screen x=100. The current [30,70] output with these displayed
coordinates is consistent with screen x=100.

Prediction: moving the prop horizontally left, toward the light, will
increase magnification and widen its shadow symmetrically about y=50.
Keeping the light and prop y endpoints fixed, reaching prop x=40 should
produce [25, 75], length50, and satisfy Single Gate. Each endpoint is ten
units from the light's height, multiplied by 100/40=2.5.

I will select prop1 and use the left-arrow keyboard control, observing its
movement increment rather than assuming an undocumented step size. The
prediction of the target geometry is fixed before that first adjustment.
The first left-arrow press should widen the interval if it moves the prop
left. I have not assumed an exact first-step interval until I know the
control's actual increment.
