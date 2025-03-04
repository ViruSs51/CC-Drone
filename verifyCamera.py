import cv2
import os
from utils import FileManager


config_path = "data/config.json"


def get_avaible_cams() -> list[str]:
    cams = ["drone"]

    for i in range(15):
        cap = cv2.VideoCapture(i)

        if cap.isOpened():
            print(i)
            cams.append(str(i))
            cap.release()

    return cams


def main():
    config = FileManager.open_json(filename=config_path)

    cams = get_avaible_cams()
    os.system("cls")

    while True:
        print(f'List of available camera index: {", ".join(cams)}')
        camera_index = input("Choose the camera index you want to use: ")

        if camera_index in cams:
            try:
                config["camera"] = (
                    int(camera_index) if camera_index != "drone" else camera_index
                )
                FileManager.write_json(filename=config_path, content=config)

                print("\nThe camera has been set up successfully!\n")
                break

            except Exception as err:
                print(f"\nERROR: {err}\n")
                continue

        else:
            print("\nIncorrect camera index!\n")

    if config["camera"] != "drone":
        cap = cv2.VideoCapture(config["camera"])
        print("Press any key to close the window!\n")
        while True:
            ret, frame = cap.read()

            if not ret:
                print("\nCould not gain access to the camera!\n")
                break

            cv2.imshow("Camera", frame)

            if cv2.waitKey(1) != -1:
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
