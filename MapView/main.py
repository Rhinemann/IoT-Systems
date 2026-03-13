import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapview = None
        self.datasource = Datasource(user_id=1)
        self.line_layer = None
        self.car_marker = None

        # додати необхідні змінні
        self.bump_markers = []
        self.pothole_markers = []

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        Clock.schedule_once(lambda dt: self.set_bump_marker((50.4501, 30.5234)), 0)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        new_points = self.datasource.get_new_points()

        if not new_points:
            return

        for point in new_points:

            lat, lon, road_state = point

            # Оновлює лінію маршрута
            self.line_layer.add_point((lat, lon))

            # Оновлює маркер маниши
            self.update_car_marker((lat, lon))

            # Перевіряємо стан дороги
            self.check_road_quality(point)

    def check_road_quality(self, point):
        """
        Аналізує дані акселерометра для подальшого визначення
        та відображення ям та лежачих поліцейських
        """
        if len(point) < 3:
            return

        lat, lon, road_state = point

        if road_state == "pothole":
            self.set_pothole_marker((lat, lon))
        elif road_state == "bump":
            self.set_bump_marker((lat, lon))

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        lat, lon = point[0], point[1]

        if not self.car_marker:
            self.car_marker = MapMarker(lat=lat, lon=lon, source='./images/car')
            self.mapview.add_marker(self.car_marker)
        else:
            self.car_marker.lat = lat
            self.car_marker.lon = lon

        self.mapview.center_on(lat, lon)

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
            source="images/bump.png"  
        )

        self.mapview.add_marker(marker)
        self.bump_markers.append(marker)


    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView(
            zoom=15,
            lat=50.4501,
            lon=30.5234
        )

        self.line_layer = LineMapLayer()
        self.mapview.add_layer(self.line_layer)

        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
