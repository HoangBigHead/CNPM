import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Auto Login',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        appBarTheme: AppBarTheme(
          elevation: 0,
          centerTitle: true,
        ),
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final urlController = TextEditingController();
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  final usernameFieldIdController = TextEditingController();
  final passwordFieldIdController = TextEditingController();
  final loginButtonIdController = TextEditingController();

  String statusMessage = "Chưa bắt đầu";
  List<dynamic> websites = [];

  static const String baseUrl = 'http://127.0.0.1:8000';

  @override
  void initState() {
    super.initState();
    fetchWebsites();
  }

  void updateStatus(String message) {
    setState(() {
      statusMessage = message;
    });
  }

  Future<void> fetchWebsites() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/website-credentials/load/'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data.containsKey('websites')) {
          setState(() {
            websites = data['websites'];
          });
          updateStatus("Tải danh sách website thành công");
        } else {
          updateStatus("Không có dữ liệu websites.");
        }
      } else {
        updateStatus("Tải danh sách website thất bại");
      }
    } catch (e) {
      updateStatus("Lỗi: ${e.toString()}");
    }
  }

  Future<void> addWebsite() async {
    final url = urlController.text.trim();
    final username = usernameController.text.trim();
    final password = passwordController.text.trim();
    final usernameFieldId = usernameFieldIdController.text.trim();
    final passwordFieldId = passwordFieldIdController.text.trim();
    final loginButtonId = loginButtonIdController.text.trim();

    if (url.isEmpty || username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Vui lòng điền đầy đủ thông tin"),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    try {
      updateStatus("Đang thêm website...");
      final response = await http.post(
        Uri.parse('$baseUrl/website-credentials/add_website/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'url': url,
          'username': username,
          'password': password,
          'username_field_id': usernameFieldId,
          'password_field_id': passwordFieldId,
          'login_button_id': loginButtonId
        }),
      );

      if (response.statusCode == 201) {
        updateStatus("Thêm website thành công");
        fetchWebsites();
        urlController.clear();
        usernameController.clear();
        passwordController.clear();
        usernameFieldIdController.clear();
        passwordFieldIdController.clear();
        loginButtonIdController.clear();
      } else {
        updateStatus("Thêm website thất bại");
      }
    } catch (e) {
      updateStatus("Lỗi: ${e.toString()}");
    }
  }

  Future<void> deleteWebsite(int id) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/website-credentials/delete_website/?id=$id'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 204) {
        updateStatus("Xóa website thành công");
        fetchWebsites();
      } else {
        updateStatus("Xóa website thất bại");
      }
    } catch (e) {
      updateStatus("Lỗi: ${e.toString()}");
    }
  }

  Future<void> startAutoLogin(int websiteId) async {
    try {
      updateStatus("Đang khởi động trình duyệt...");

      final response = await http.post(
        Uri.parse('$baseUrl/website-credentials/auto_login/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        updateStatus("Quá trình tự động đăng nhập đã bắt đầu!");
      } else if (response.statusCode == 400) {
        updateStatus("Yêu cầu không hợp lệ. Vui lòng kiểm tra lại thông tin.");
      } else if (response.statusCode == 404) {
        updateStatus("Không tìm thấy website với ID $websiteId.");
      } else {
        updateStatus("Không thể bắt đầu tự động đăng nhập.");
      }
    } catch (e) {
      updateStatus("Lỗi: ${e.toString()}");
    }
  }

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width < 500;

    return Scaffold(
      appBar: AppBar(
        title: Text("Tự Động Đăng Nhập"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: isMobile
            ? Column(
          children: [
            Expanded(child: buildInputForm()),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => WebsiteListPage(websites: websites, deleteWebsite: deleteWebsite),
                  ),
                );
              },
              child: Text("Các Website Đã Lưu"),
            ),
          ],
        )
            : Row(
          children: [
            Expanded(flex: 2, child: buildInputForm()),
            Expanded(flex: 3, child: buildWebsiteList()),
          ],
        ),
      ),
    );
  }

  Widget buildInputForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            statusMessage,
            style: TextStyle(fontSize: 16, color: Colors.blue.shade700),
            textAlign: TextAlign.center,
          ),
        ),
        SizedBox(height: 10),
        TextField(
          controller: urlController,
          decoration: InputDecoration(
            labelText: "URL",
            prefixIcon: Icon(Icons.web),
            border: OutlineInputBorder(),
          ),
        ),
        SizedBox(height: 10),
        TextField(
          controller: usernameController,
          decoration: InputDecoration(
            labelText: "Tên đăng nhập",
            prefixIcon: Icon(Icons.person),
            border: OutlineInputBorder(),
          ),
        ),
        SizedBox(height: 10),
        TextField(
          controller: passwordController,
          decoration: InputDecoration(
            labelText: "Mật khẩu",
            prefixIcon: Icon(Icons.lock),
            border: OutlineInputBorder(),
          ),
          obscureText: true,
        ),
        SizedBox(height: 10),
        TextField(
          controller: usernameFieldIdController,
          decoration: InputDecoration(
            labelText: "ID ô nhập tên đăng nhập (tùy chọn)",
            border: OutlineInputBorder(),
          ),
        ),
        SizedBox(height: 10),
        TextField(
          controller: passwordFieldIdController,
          decoration: InputDecoration(
            labelText: "ID ô nhập mật khẩu (tùy chọn)",
            border: OutlineInputBorder(),
          ),
        ),
        SizedBox(height: 10),
        TextField(
          controller: loginButtonIdController,
          decoration: InputDecoration(
            labelText: "ID nút đăng nhập (tùy chọn)",
            border: OutlineInputBorder(),
          ),
        ),
        SizedBox(height: 20),
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: addWebsite,
                icon: Icon(Icons.add),
                label: Text("Thêm Website"),
              ),
            ),
            SizedBox(width: 10),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: websites.isNotEmpty
                    ? () => startAutoLogin(websites[0]['id'])
                    : null,
                icon: Icon(Icons.play_arrow),
                label: Text("Bắt Đầu"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget buildWebsiteList() {
    return websites.isEmpty
        ? Center(child: Text("Chưa có website nào"))
        : ListView.builder(
      itemCount: websites.length,
      itemBuilder: (context, index) {
        final website = websites[index];
        return Card(
          elevation: 2,
          margin: EdgeInsets.symmetric(vertical: 5),
          child: ListTile(
            title: Text(website['url'],
                style: TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(website['username']),
            trailing: IconButton(
              icon: Icon(Icons.delete, color: Colors.red),
              onPressed: () => deleteWebsite(website['id']),
            ),
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    urlController.dispose();
    usernameController.dispose();
    passwordController.dispose();
    usernameFieldIdController.dispose();
    passwordFieldIdController.dispose();
    loginButtonIdController.dispose();
    super.dispose();
  }
}

class WebsiteListPage extends StatelessWidget {
  final List<dynamic> websites;
  final Function(int) deleteWebsite;

  WebsiteListPage({required this.websites, required this.deleteWebsite});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Danh Sách Website"),
      ),
      body: websites.isEmpty
          ? Center(child: Text("Chưa có website nào"))
          : ListView.builder(
        itemCount: websites.length,
        itemBuilder: (context, index) {
          final website = websites[index];
          return Card(
            elevation: 2,
            margin: EdgeInsets.symmetric(vertical: 5),
            child: ListTile(
              title: Text(website['url'],
                  style: TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(website['username']),
              trailing: IconButton(
                icon: Icon(Icons.delete, color: Colors.red),
                onPressed: () => deleteWebsite(website['id']),
              ),
            ),
          );
        },
      ),
    );
  }
}
