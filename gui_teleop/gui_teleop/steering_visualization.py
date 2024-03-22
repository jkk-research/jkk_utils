import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from sensor_msgs.msg import Joy
from pacmod3_msgs.msg import VehicleSpeedRpt, SteeringAuxRpt, SteeringCmd
import pygame
import math

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.screen_width = 600
        self.screen_height = 400

        self.init_pygame()
        self.init_subscriptions()

        self.last_driving_status = None
        self.last_reference_speed = None
        self.last_current_speed = None
        self.last_steering_angle = None
        self.last_current_steering_angle=None
        self.throttle=None
        
    def init_pygame(self):
        pygame.init()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        pygame.display.set_caption("ROS2 Data Visualization")
        self.font = pygame.font.SysFont(None, 36)
        # self.steering_wheel_image.set_alpha(180)
        
    def init_subscriptions(self):
        self.subscription = self.create_subscription(Bool, '/lexus3/pacmod/enabled', self.check_control, 10)
        # self.subscription1 = self.create_subscription(Twist, '/lexus3/cmd_vel', self.listener_callback1, 10)
        
        self.subscription2 = self.create_subscription(VehicleSpeedRpt, '/lexus3/pacmod/vehicle_speed_rpt', self.vehicle_speed_listener, 10)
        self.subscription3 = self.create_subscription(SteeringAuxRpt, '/lexus3/pacmod/steering_aux_rpt', self.current_steering_listener, 10)
        self.subscription4 = self.create_subscription(SteeringCmd, '/lexus3/pacmod/steering_cmd', self.ref_steering_listener, 10)
        self.subscription4 = self.create_subscription(Joy, '/joy', self.joystick_listener, 10)

    def update_display(self):
        self.screen.fill((0, 0, 0))

        if self.last_driving_status is not None:
            text = self.font.render(self.last_driving_status, True, (107, 195, 53) if self.last_driving_status.startswith('You') else (220, 38, 38))
            self.screen.blit(text, (200, 20))

        if self.last_reference_speed is not None:
            text = self.font.render('Reference Speed: {:.2f}Km/h'.format(self.last_reference_speed), True, (107, 195, 53))
            self.screen.blit(text, (150, 70))

        if self.last_current_speed is not None:
            text = self.font.render('Current Speed: {:.2f}Km/h'.format(self.last_current_speed), True, (220, 38, 38))
            self.screen.blit(text, (150, 50))
            
        
        if self.last_current_steering_angle is not None:
            self.draw_steering_wheel((self.screen_width // 2, self.screen_height // 2), self.last_current_steering_angle)
            
        if self.last_steering_angle is not None:
            self.draw_ref_steering_wheel((self.screen_width // 2, self.screen_height // 2), self.last_steering_angle)
            
        if self.throttle is not None:
            self.draw_bar(self.throttle)
        
        pygame.display.flip()  

    def draw_steering_wheel(self, position, angle):
        wheel_radius = 100
        inner_wheel_radius = 30
        inner_wheel_color = (255, 255, 255)
        rim_color = (255, 255, 255)
        line_color = (255, 0, 0)


        vertical_0_start = self.rotate_point(position, angle, -inner_wheel_radius)
        vertical_0_end = self.rotate_point(position, angle, -wheel_radius)
        horizontal_0_start = self.rotate_point(position, angle + 90, inner_wheel_radius)  # Adjust angle for horizontal lines
        horizontal_0_end = self.rotate_point(position, angle + 90, wheel_radius)
        horizontal_0a_start = self.rotate_point(position, angle - 90, inner_wheel_radius)
        horizontal_0a_end = self.rotate_point(position, angle - 90, wheel_radius)
        horizontal_1_start = self.rotate_point(position, angle + 90, wheel_radius)
        horizontal_1_end = self.rotate_point(position, angle + 90, wheel_radius)
        horizontal_1a_start = self.rotate_point(position, angle - 90, wheel_radius)
        horizontal_1a_end = self.rotate_point(position, angle - 90, wheel_radius)

        # Draw elements using calculated coordinates
        pygame.draw.circle(self.screen, inner_wheel_color, position, inner_wheel_radius, 4)
        pygame.draw.circle(self.screen, rim_color, position, wheel_radius, 4)
        pygame.draw.line(self.screen, line_color, vertical_0_start, vertical_0_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_0_start, horizontal_0_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_0a_start, horizontal_0a_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_1_start, horizontal_1_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_1a_start, horizontal_1a_end,3)

        text = self.font.render('Current angle: {:.2f}°'.format(angle), True, (255, 0, 0))
        self.screen.blit(text, (325, 300))


    def draw_ref_steering_wheel(self, position, angle):
        wheel_radius = 100
        inner_wheel_radius = 30
        inner_wheel_color = (255,255,255)
        rim_color = (255, 255, 255)
        line_color = (0, 0, 255)

        vertical_0_start = self.rotate_point(position, angle, -inner_wheel_radius)
        vertical_0_end = self.rotate_point(position, angle, -wheel_radius)
        horizontal_0_start = self.rotate_point(position, angle + 90, inner_wheel_radius)  # Adjust angle for horizontal lines
        horizontal_0_end = self.rotate_point(position, angle + 90, wheel_radius)
        horizontal_0a_start = self.rotate_point(position, angle - 90, inner_wheel_radius)
        horizontal_0a_end = self.rotate_point(position, angle - 90, wheel_radius)
        horizontal_1_start = self.rotate_point(position, angle + 90, wheel_radius)
        horizontal_1_end = self.rotate_point(position, angle + 90, wheel_radius)
        horizontal_1a_start = self.rotate_point(position, angle - 90, wheel_radius)
        horizontal_1a_end = self.rotate_point(position, angle - 90, wheel_radius)

        # Draw elements using calculated coordinates
        pygame.draw.circle(self.screen, inner_wheel_color, position, inner_wheel_radius, 4)
        pygame.draw.circle(self.screen, rim_color, position, wheel_radius, 4)
        pygame.draw.line(self.screen, line_color, vertical_0_start, vertical_0_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_0_start, horizontal_0_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_0a_start, horizontal_0a_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_1_start, horizontal_1_end,3)
        pygame.draw.line(self.screen, line_color, horizontal_1a_start, horizontal_1a_end,3)
        
        text = self.font.render('Ref angle: {:.2f}°'.format(angle), True, (0, 0, 255))
        self.screen.blit(text, (325, 340))

    def draw_bar(self,level):
        bar_x = 50
        bar_y = 100
        bar_width = 50
        bar_height = 200
        bar_color = (255, 255, 255)  # White background
        zero_color=(184,184,184)
        acc_color = (0, 255, 0)  # Green for acceleration
        braking_color = (255, 0, 0)  # Red for braking

        throttle_percentage = -level / bar_height * 100

        color = acc_color if throttle_percentage >= 0 else braking_color

        display_percentage = min(100, abs(throttle_percentage))

        half_bar_height = bar_height // 2
        bar_top = bar_y + half_bar_height - (display_percentage / 100 * bar_height)
        bar_bottom = bar_y + half_bar_height - (-display_percentage / 100 * bar_height)

        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.line(self.screen,zero_color,(bar_x*0.6,bar_y+bar_height//2),(bar_x*2.3,bar_y+bar_height//2),2)
        
        zero_point = self.font.render('0', True, zero_color)
        self.screen.blit(zero_point, (bar_x*1.7+bar_width, 190))

        inner_bar_height = display_percentage / 100 * bar_height
        
        pygame.draw.rect(self.screen, color, (bar_x, bar_top, bar_width, inner_bar_height)) if throttle_percentage>=0 else pygame.draw.rect(self.screen, color, (bar_x, bar_bottom, bar_width, inner_bar_height))
        
        full_text=self.font.render('1', True, acc_color)
        self.screen.blit(full_text, (bar_x+bar_width//2-10, bar_y*1.2-bar_x))
        
        full_brake_text=self.font.render('-1', True, braking_color)
        self.screen.blit(full_brake_text, (bar_x+bar_width//2-10, bar_y*1.1+bar_height))

        text = self.font.render('Joystick:{:.2f}%'.format(throttle_percentage), True, acc_color)
        self.screen.blit(text, (bar_x//2, bar_y*1.35+bar_height))

    def rotate_point(self,center, angle, radius):
        angle_radians = math.radians(angle)
        x = center[0] + radius * math.cos(angle_radians)
        y = center[1] - radius * math.sin(angle_radians)
        return (int(x), int(y))

    def check_control(self, msg):  
        self.last_driving_status = 'You Are Driving' if msg.data else 'In Car Driver'
        self.update_display()

    def listener_callback1(self, msg):

        self.last_reference_speed = msg.linear.x
        self.update_display()

    def vehicle_speed_listener(self, msg):
        self.last_current_speed = msg.vehicle_speed
        self.update_display()

    def current_steering_listener(self, msg):
        self.last_current_steering_angle = math.degrees(msg.rotation_rate)
        self.update_display()

    def ref_steering_listener(self, msg):
        self.last_steering_angle = math.degrees(msg.command)
        self.update_display()
        
    def joystick_listener(self, msg):
        self.throttle = math.degrees(msg.axes[0])
        self.update_display()
        

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()
    pygame.quit()

if __name__ == '__main__':
    
    main()