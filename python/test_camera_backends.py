import cv2

backends = [(cv2.CAP_DSHOW,'DSHOW'), (cv2.CAP_MSMF,'MSMF'), (cv2.CAP_ANY,'ANY')]
for backend, name in backends:
    print(f"--- Probando backend {name} ({backend}) ---")
    for i in range(6):
        try:
            cap = cv2.VideoCapture(i, backend)
        except Exception:
            cap = cv2.VideoCapture(i)
        ok = cap.isOpened()
        ret = False
        if ok:
            ret, _ = cap.read()
        print(f"{name} index={i} opened={ok} read={ret}")
        cap.release()