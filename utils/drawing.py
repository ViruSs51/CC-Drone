import numpy as np
import cv2


class MathDrawing:
    def bresenham(self, x0, y0, x1, y1):
        pixels = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            pixels.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return pixels

    def calculateLineByAngle(self, x0, y0, length, angle) -> list[tuple[int]]:
        angle_rad = np.radians(angle)
        x1 = x0 + int(length * np.cos(angle_rad))
        y1 = y0 + int(length * np.sin(angle_rad))

        return self.bresenham(x0, y0, x1, y1)

    def drawLine(self, frame: np.ndarray, points: list[tuple[int]], color: list[int] | tuple[int]):
        for p in points:
            cv2.rectangle(frame, p, (p[0]+1, p[1]+1), color, 10)

    def drawMinimapOnFrame(self, frame1: np.ndarray, frame2: np.ndarray, position: list[int] | tuple[int], size: list[int] | tuple[int]) -> np.ndarray:
        frame2 = cv2.flip(frame2, 0)
        frame2 = cv2.resize(frame2.copy(), (size*2, size*2))
        frame2_size = frame2.shape

        for r in range(size, frame1.shape[1]):
            cv2.circle(frame2, (frame2_size[1]//2, frame2_size[0]//2), r, (0, 0, 0), 2)

        mask1 = cv2.inRange(frame2, (1, 0, 0), (255, 255, 255))
        mask2 = cv2.inRange(frame2, (0, 1, 0), (255, 255, 255))
        mask3 = cv2.inRange(frame2, (0, 0, 1), (255, 255, 255))

        y1, y2 = position[1], position[1] + frame2.shape[0]
        x1, x2 = position[0], position[0] + frame2.shape[1]
        roi = frame1[y1:y2, x1:x2]
    
        roi[mask1 > 0] = frame2[mask1 > 0]
        roi[mask2 > 0] = frame2[mask2 > 0]
        roi[mask3 > 0] = frame2[mask3 > 0]
        
        frame1[y1:y2, x1:x2] = roi

        cv2.circle(frame1, (position[0]+frame2_size[0]//2, position[1]+frame2_size[1]//2), size, (0, 0, 0), 2)
    
        return frame1
