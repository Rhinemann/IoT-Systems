import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        # додати необхідні змінні

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """


    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        lat, lon = point[0], point[1]

        if not hasattr(self, 'car_marker'):
            self.car_marker = MapMarker(lat=lat, lon=lon, source='./images/car')
            self.mapview.add_marker(self.car_marker)
        else:
            self.car_marker.lat = lat
            self.car_marker.lon = lon

        self.mapview.center_on(lat, lon)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView()
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
