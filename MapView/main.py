import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource

line_layer_colors = [
    [1, 0, 0, 1],
    [1, 0.5, 0, 1],
    [0, 1, 0, 1],
    [0, 1, 1, 1],
    [0, 0, 1, 1],
    [1, 0, 1, 1],
]

class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapview = None
        self.datasource = Datasource(user_id=1)
        self.line_layers = dict()
        self.car_markers = dict()

        # додати необхідні змінні
        self.bump_markers = []
        self.pothole_markers = []

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.update()
        Clock.schedule_interval(self.update, 5)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        new_points = self.datasource.get_new_points()

        if not new_points:
            return

        for point in new_points:

            lat, lon, road_state, user_id = point

            # Оновлює лінію маршрута
            if user_id not in self.line_layers:
                self.line_layers[user_id] = LineMapLayer(color = line_layer_colors[user_id])
                self.mapview.add_layer(self.line_layers[user_id])

            self.line_layers[user_id].add_point((lat, lon))

            # Оновлює маркер маниши
            self.update_car_marker(lat, lon, user_id)

            # Перевіряємо стан дороги
            self.check_road_quality(point)

    def check_road_quality(self, point):
        """
        Аналізує дані акселерометра для подальшого визначення
        та відображення ям та лежачих поліцейських
        """
        if len(point) < 3:
            return

        lat, lon, road_state, user_id = point

        if road_state == "pothole":
            self.set_pothole_marker((lat, lon))
        elif road_state == "bump":
            self.set_bump_marker((lat, lon))

    def update_car_marker(self, lat, lon, user_id):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        if user_id not in self.car_markers:
            self.car_markers[user_id] = MapMarker(lat=lat, lon=lon, source='./images/car.png')
            self.mapview.add_marker(self.car_markers[user_id])
        else:
            self.car_markers[user_id].lat = lat
            self.car_markers[user_id].lon = lon

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

        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
