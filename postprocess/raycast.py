import math

class Raycast:

    def __init__(self, heading, pitch, norm_screen_x, norm_screen_y, fovy, aspect):
        # screen_x, screen_y: normalized (-1~1), aspect: width/height
        self.heading = heading
        self.pitch = pitch
        self.screen_x = norm_screen_x
        self.screen_y = norm_screen_y
        self.fovy = fovy
        self.aspect = aspect

    def get_raycast(self):
        return {'pitch': self.pitch + 0.5 * self.screen_y * self.fovy / self.aspect ,
        'heading': self.heading + 0.5 * self.screen_x * self.fovy}

    def get_distance(self,observer_height): # if the raycast intersect with the ground
        theta = self.get_raycast()['pitch']
        if -1 > theta and theta > -89:
            return abs(observer_height/math.tan(theta/180.0*math.pi))
        else:
            return None

    def get_latlng(self,current_lat, current_lng,cam_height=2):
        heading = ((360 - self.get_raycast()['heading']) + 90)%360
        distance = self.get_distance(cam_height)
        if distance is None:
            return None
        x = distance * math.cos(heading/180.0*math.pi)
        y = distance * math.sin(heading/180.0*math.pi)
        return {'lat': current_lat + y/111300.0,
        'lng': current_lng + x/111300.0/math.cos(current_lat/180.0*math.pi)}
