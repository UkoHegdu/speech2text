# Restarts the USB hub feeding the webcam mic (Logitech Brio 100), which gets
# stuck suspended by the Dell monitor's built-in hub chain. Run elevated —
# installed as a scheduled task (Speech2Text_USBRecover) so the app can
# trigger it without a UAC prompt each time. See memory: project_usb_mic_hub_chain.
pnputil /restart-device "USB\VID_05E3&PID_0608\6&26c36cb0&0&1"
