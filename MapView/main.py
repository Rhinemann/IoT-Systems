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
        self.pothole_markers = []

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

    def set_pothole_marker(self, point):
        if isinstance(point, dict):
            lat = point.get("lat")
            lon = point.get("lon")
        else:
            lat, lon = point

        if lat is None or lon is None:
            return
        
        marker = MapMarker(
            lat=lat,
            lon=lon,
            source="images/pothole.png"  
        )

        self.mapview.add_marker(marker)
        self.pothole_markers.append(marker)

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
