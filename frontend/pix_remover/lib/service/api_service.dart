import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://10.0.2.2:8000";

  static Future<Uint8List> removeBackground(File image) async {
    var request = http.MultipartRequest(
      "POST",
      Uri.parse("$baseUrl/remove-background"),
    );

    request.files.add(await http.MultipartFile.fromPath("file", image.path));

    final response = await request.send();

    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception("Remove background gagal");
    }
  }
}
