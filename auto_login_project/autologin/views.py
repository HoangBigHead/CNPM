import time
import threading
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import WebsiteCredentials
from .serializers import WebsiteCredentialsSerializer
import mysql.connector
import json
from django.core.exceptions import ValidationError
# Kết nối với cơ sở dữ liệu MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      
        user="root",           
        password="123456789",
        database="AutoLogin_DB",
        port=3308
    )

class WebsiteCredentialsViewSet(viewsets.ModelViewSet):
    queryset = WebsiteCredentials.objects.all()
    serializer_class = WebsiteCredentialsSerializer

    def validate_url(self, url):
        # Basic URL validation
        if not url or not (url.startswith('http://') or url.startswith('https://')):
            raise ValidationError("URL không hợp lệ. Phải bắt đầu bằng http:// hoặc https://")
        return url
    # Load tất cả website credentials từ DB
    def load_website_credentials(self):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM autologin_db.autologin_websitecredentials;")
        websites = cursor.fetchall()
        connection.close()
        return websites
    
    # Lưu thông tin website credentials vào DB
    def save_website_credentials(self, new_entry):
        # Validate input
        validated_url = self.validate_url(new_entry.get('url'))
        
        # Kiểm tra các trường bắt buộc
        required_fields = ['username', 'password']
        for field in required_fields:
            if not new_entry.get(field):
                raise ValidationError(f"Trường {field} không được để trống")

        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO autologin_db.autologin_websitecredentials 
            (url, username, password, username_field_id, password_field_id, login_button_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (
            validated_url, 
            new_entry['username'], 
            new_entry['password'],
            new_entry.get('username_field_id', ''),  # Cho phép để trống
            new_entry.get('password_field_id', ''),  # Cho phép để trống
            new_entry.get('login_button_id', '')     # Cho phép để trống
        )
        
        try:
            cursor.execute(query, data)
            connection.commit()
            
            # Lấy ID của bản ghi vừa được thêm
            new_website_id = cursor.lastrowid
            
            print("Thông tin đã được lưu vào cơ sở dữ liệu.")
            connection.close()
            
            return new_website_id
        except mysql.connector.Error as err:
            connection.close()
            raise ValidationError(f"Lỗi khi lưu vào cơ sở dữ liệu: {err}")
    @action(detail=False, methods=['post'])
    def add_website(self, request):
        try:
        # Lấy dữ liệu từ request
            data = json.loads(request.body)
        
        # Validate URL
            validated_url = self.validate_url(data['url'])
        
        # Nếu không có ID của các trường, tự động tìm kiếm
            if not (data.get('username_field_id') and data.get('password_field_id') and data.get('login_button_id')):
            # Khởi tạo trình duyệt
                driver = webdriver.Chrome()
            
                try:
                # Truy cập URL
                    driver.get(validated_url)
                
                # Tìm kiếm các trường đăng nhập
                    username_field, password_field, login_button = self.identify_fields(driver)
                
                # Lấy ID của các trường
                    username_field_id = username_field.get_attribute('id') if username_field else ''
                    password_field_id = password_field.get_attribute('id') if password_field else ''
                    login_button_id = login_button.get_attribute('id') if login_button else ''
            
                except NoSuchElementException as e:
                # Nếu không tìm thấy các trường, đóng trình duyệt và báo lỗi
                    driver.quit()
                    return Response({
                        'message': f'Không thể tự động xác định các trường đăng nhập: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
                finally:
                # Đảm bảo đóng trình duyệt
                    driver.quit()
            else:
            # Sử dụng các ID được cung cấp sẵn
                username_field_id = data.get('username_field_id', '')
                password_field_id = data.get('password_field_id', '')
                login_button_id = data.get('login_button_id', '')
        
        # Thêm thông tin vào cơ sở dữ liệu
            new_entry = {
                'url': validated_url,
                'username': data['username'],
                'password': data['password'],
                'username_field_id': username_field_id,
                'password_field_id': password_field_id,
                'login_button_id': login_button_id
            }
        
        # Thêm website vào cơ sở dữ liệu
            new_website_id = self.save_website_credentials(new_entry)
        
        # Trả về phản hồi thành công
            return Response({
                'message': 'Thêm website thành công', 
                'website_id': new_website_id,
                'username_field_id': username_field_id,
                'password_field_id': password_field_id,
                'login_button_id': login_button_id
            }, status=status.HTTP_201_CREATED)
    
        except ValidationError as ve:
        # Xử lý lỗi xác thực
            return Response({
            'message': str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)
    
        except json.JSONDecodeError:
        # Lỗi khi không thể parse JSON
            return Response({
            'message': 'Dữ liệu không hợp lệ'
            }, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
        # Xử lý các lỗi không mong muốn
            return Response({
            'message': f'Lỗi không xác định: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @action(detail=False, methods=['delete'])
    def delete_website(self, request):
        try:
            # Lấy ID website từ request hoặc query params
            website_id = request.query_params.get('id')
            
            if not website_id:
                return Response({
                    'message': 'Vui lòng cung cấp ID website'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Xóa website theo ID
            query = "DELETE FROM autologin_db.autologin_websitecredentials WHERE id = %s"
            cursor.execute(query, (website_id,))
            connection.commit()
            
            # Kiểm tra xem có bản ghi nào bị xóa không
            if cursor.rowcount == 0:
                connection.close()
                return Response({
                    'message': f'Không tìm thấy website với ID {website_id}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            connection.close()
            
            return Response({
                'message': 'Xóa website thành công'
            }, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({
                'message': f'Lỗi khi xóa website: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # Hàm tìm kiếm an toàn phần tử trên trang web
    def find_element_safe(self, driver, by, value):
        try:
            return driver.find_element(by, value)
        except NoSuchElementException:
            print(f"Không tìm thấy phần tử: {value}")
            return None

    # Hàm xác định các trường đăng nhập tự động
    def identify_fields(self, driver):
        time.sleep(3)  # Chờ trang web tải
        username_field, password_field, login_button = None, None, None

        possible_username_xpaths = [
            "//input[contains(@type, 'text') or contains(@type, 'email')]",
            "//input[contains(@id, 'user') or contains(@id, 'name') or contains(@placeholder, 'Tên đăng nhập') or contains(@placeholder, 'Username')]",
            "//input[contains(@aria-label, 'Username') or contains(@aria-label, 'Email')]",
        ]
        for xpath in possible_username_xpaths:
            try:
                username_field = driver.find_element(By.XPATH, xpath)
                break
            except NoSuchElementException:
                continue

        possible_password_xpaths = [
            "//input[@type='password']",
            "//input[contains(@id, 'pass') or contains(@placeholder, 'Mật khẩu')]",
            "//input[contains(@aria-label, 'Password')]",
        ]
        for xpath in possible_password_xpaths:
            try:
                password_field = driver.find_element(By.XPATH, xpath)
                break
            except NoSuchElementException:
                continue

        possible_login_xpaths = [
            "//button[contains(text(), 'Đăng nhập') or contains(text(), 'Login')]",
            "//input[@type='submit' or @value='Login' or @value='Đăng nhập']",
            "//button[@type='submit']",
        ]
        for xpath in possible_login_xpaths:
            try:
                login_button = driver.find_element(By.XPATH, xpath)
                break
            except NoSuchElementException:
                continue

        if not username_field or not password_field or not login_button:
            raise NoSuchElementException("Không tìm thấy các trường đăng nhập hoặc nút đăng nhập.")
    
        return username_field, password_field, login_button

    # Hàm tự động đăng nhập
    def perform_auto_login(self, driver, website):
        def update_status(message):
            print(message)  # In ra thông báo trạng thái (hoặc trả về phản hồi nếu cần)

        update_status(f"Tự động đăng nhập vào {website['url']}...")
        try:
            driver.get(website['url'])
            username_field, password_field, login_button = self.identify_fields(driver)
            username_field.send_keys(website['username'])
            password_field.send_keys(website['password'])
            login_button.click()
            update_status("Đã đăng nhập thành công!")
        except Exception as e:
            update_status(f"Lỗi khi tự động đăng nhập: {e}")

    # Hàm khởi động trình duyệt và kiểm tra URL
    def start_browser(self):
        def update_status(message):
            print(message)

        websites = self.load_website_credentials()

        if not websites:
            update_status("Không có dữ liệu trong Database")
            return None, None

        # Mở trình duyệt với một trang web mặc định
        driver = webdriver.Chrome()
        driver.get("https://www.google.com")  # Khởi tạo với một URL hợp lệ
        update_status("Trình duyệt đã khởi động. Đang mở trang Google.")
        
        return driver, websites

    # Action để load tất cả website credentials từ DB
    @action(detail=False, methods=['get'])
    def load(self, request):        
        websites = self.load_website_credentials()        
        return Response({"websites": websites})

    # Action để tự động đăng nhập cho một website cụ thể
    @action(detail=False, methods=['post'])
    def auto_login(self, request):
        # Gọi hàm start_browser để khởi động trình duyệt và lấy thông tin website từ DB
        driver, websites = self.start_browser()

        if not driver:
            return Response({"message": "Không thể khởi động trình duyệt hoặc không có dữ liệu website."}, status=400)

        try:
            while True:
                # Lấy URL hiện tại từ thanh địa chỉ của trình duyệt
                current_url = driver.current_url
                print(f"URL hiện tại: {current_url}")

                # Kiểm tra URL với danh sách các trang web đã lưu
                for website in websites:
                    if current_url.startswith(website['url']):
                        print(f"URL khớp: {current_url}. Đang thực hiện đăng nhập...")
                        self.perform_auto_login(driver, website)
                        time.sleep(5)  # Đợi để đảm bảo login hoàn tất
                        break

                time.sleep(2)

        except Exception as e:
            print(f"Lỗi khi chạy auto_login: {e}")
            return Response({"error": f"Lỗi khi chạy auto_login: {e}"}, status=500)

        finally:
            driver.quit()
            print("Trình duyệt đã đóng.")

            return Response({"message": "Quá trình tự động đăng nhập hoàn tất."})
    