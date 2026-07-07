import cv2


def obtener_centroid(contorno):
    momentos = cv2.moments(contorno)
    if momentos['m00'] == 0:
        return None
    cx = int(momentos['m10'] / momentos['m00'])
    cy = int(momentos['m01'] / momentos['m00'])
    return cx, cy
