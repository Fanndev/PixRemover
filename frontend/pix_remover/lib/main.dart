import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: Colors.grey[100],
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            elevation: 4,
          ),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
          elevation: 4,
        ),
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  File? imageFile;
  Uint8List? webBytes;
  Uint8List? resultBytes;
  bool loading = false;
  String? errorMessage;

  String apiUrl = kIsWeb
      ? "http://localhost:8000/remove-background"
      : "http://10.0.2.2:8000/remove-background";

  Future<void> pickImage() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (picked != null) {
      webBytes = await picked.readAsBytes();
      if (!kIsWeb) imageFile = File(picked.path);
      resultBytes = null;
      errorMessage = null;
      setState(() {});
    }
  }

  Future<void> removeBg() async {
    if (webBytes == null) return;

    setState(() {
      loading = true;
      errorMessage = null;
    });

    final uri = Uri.parse(apiUrl);

    final request = http.MultipartRequest('POST', uri);
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      webBytes!,
      filename: 'image.png',
      contentType: MediaType('image', 'png'),
    ));

    try {
      final response = await request.send();

      if (response.statusCode == 200) {
        resultBytes = await response.stream.toBytes();
      } else {
        errorMessage = "Failed to remove background. Status: ${response.statusCode}";
      }
    } catch (e) {
      errorMessage = "An error occurred: $e";
    }

    setState(() {
      loading = false;
    });
  }

  Widget buildImage() {
    if (resultBytes != null) {
      return Column(
        children: [
          const Text(
            "Background Removed",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green),
          ),
          const SizedBox(height: 10),
          Card(
            elevation: 8,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.memory(resultBytes!, fit: BoxFit.contain),
            ),
          ),
        ],
      );
    }
    if (kIsWeb && webBytes != null) {
      return Column(
        children: [
          const Text(
            "Original Image",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue),
          ),
          const SizedBox(height: 10),
          Card(
            elevation: 8,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.memory(webBytes!, fit: BoxFit.contain),
            ),
          ),
        ],
      );
    }
    if (!kIsWeb && imageFile != null) {
      return Column(
        children: [
          const Text(
            "Original Image",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue),
          ),
          const SizedBox(height: 10),
          Card(
            elevation: 8,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.file(imageFile!, fit: BoxFit.contain),
            ),
          ),
        ],
      );
    }
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(Icons.image_not_supported, size: 100, color: Colors.grey),
        const SizedBox(height: 16),
        const Text(
          "No image selected",
          style: TextStyle(fontSize: 18, color: Colors.grey),
        ),
        const SizedBox(height: 8),
        const Text(
          "Pick an image to get started",
          style: TextStyle(fontSize: 14, color: Colors.grey),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Pix Remover"),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Expanded(
              child: Center(
                child: SingleChildScrollView(
                  child: buildImage(),
                ),
              ),
            ),
            if (loading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 16.0),
                child: CircularProgressIndicator(),
              ),
            if (errorMessage != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: Text(
                  errorMessage!,
                  style: const TextStyle(color: Colors.red, fontSize: 16),
                  textAlign: TextAlign.center,
                ),
              ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: pickImage,
                    icon: const Icon(Icons.photo_library),
                    label: const Text("Pick Image"),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: webBytes == null || loading ? null : removeBg,
                    icon: const Icon(Icons.remove_circle_outline),
                    label: const Text("Remove BG"),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}