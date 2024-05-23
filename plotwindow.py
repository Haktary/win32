import sys
import win32api
import win32con
import win32gui
import win32ui
from PIL import Image, ImageWin


class Layer:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def draw(self, hdc):
        for element in self.elements:
            image_path, position, size = element
            image = Image.open(image_path)
            image = image.resize(size)  
            dib = ImageWin.Dib(image)
            width, height = size
            dib.draw(hdc, (position[0], position[1], position[0] + width, position[1] + height))

class Scene:
    def __init__(self, width, height):
        self.cdc = None
        self.width = width
        self.height = height
        self.layers = []

    def add_layer(self, layer):
        self.layers.append(layer)

    def plot_text(self, x, y, text):
        self.cdc.TextOut(x, y, text)

    def plot_img(self, x, y, image_path, size):
        self.layers[-1].add_element((image_path, (x, y), size))

    def on_paint(self, hWnd):
        hdc, paintStruct = win32gui.BeginPaint(hWnd)
        self.cdc = win32ui.CreateDCFromHandle(hdc)

        for layer in self.layers:
            layer.draw(self.cdc.GetHandleOutput())

        win32gui.EndPaint(hWnd, paintStruct)

class Win32Window:
    def __init__(self):
        self.hInstance = win32api.GetModuleHandle(None)
        self.className = 'SimpleWin32Window'

        wndClass = win32gui.WNDCLASS()
        wndClass.hInstance = self.hInstance
        wndClass.lpszClassName = self.className
        wndClass.lpfnWndProc = self.wndProc
        wndClass.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wndClass.hbrBackground = win32con.COLOR_WINDOW + 1
        wndClass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wndClass.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        self.classAtom = win32gui.RegisterClass(wndClass)

        self.hWnd = win32gui.CreateWindow(
            self.classAtom,
            'My Win32 Window',
            win32con.WS_OVERLAPPEDWINDOW,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            self.hInstance,
            None
        )

        self.scene_instance = Scene(width=800, height=600)

    def wndProc(self, hWnd, message, wParam, lParam):
        if message == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        elif message == win32con.WM_PAINT:
            self.scene_instance.on_paint(hWnd)
            return 0
        else:
            return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

    def run(self):
        win32gui.ShowWindow(self.hWnd, win32con.SW_SHOWNORMAL)
        win32gui.UpdateWindow(self.hWnd)
        win32gui.PumpMessages()

if __name__ == '__main__':
    window = Win32Window()

    background_layer = Layer()
    foreground_layer = Layer()

    background_layer.add_element(("background.png", (0, 0), (800, 600)))
    foreground_layer.add_element(("perso.png", (10, 10), (100, 100))) 

    window.scene_instance.add_layer(background_layer)
    window.scene_instance.add_layer(foreground_layer)

    window.run()
