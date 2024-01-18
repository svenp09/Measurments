| Supported Targets | ESP32-C3 |
| ----------------- | -------- |

# _OASIS_

*Steuern der Steckdosenleiste*
Steckdosenleiste an:
sispmctl -o 1
sispmctl -o 2
sispmctl -o 4

Steckdosenleiste aus:
sispmctl -f 1
sispmctl -f 2
sispmctl -f 3
sispmctl -f 4

*Flashen*

/proj/i4watwa/projects/playground/flash.sh

*Virtual environment for joulescope*
. ~/venv/joulescope/bin/activate

*Start juolescope ui*
python3 -m joulescope_ui

*Fusion tool*
/proj/i4watwa/projects/playground/measurements/fusion_tool.py


