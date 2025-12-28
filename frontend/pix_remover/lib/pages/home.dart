import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../service/api_service.dart';
import 'package:image_gallery_saver_plus/image_gallery_saver_plus.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  File? _image;
  Uint8List? _result;
  bool _loading = false;

  Future pickImage() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (picked != null) setState(() => _image = File(picked.path));
  }

  Future removeBg() async {
    if (_image == null) return;
    setState(() => _loading = true);
    _result = await ApiService.removeBackground(_image!);
    setState(() => _loading = false);
  }

  Future saveImage() async {
    if (_result == null) return;
    await ImageGallerySaverPlus.saveImage(
      _result!,
      name: "clearcut_${DateTime.now().millisecondsSinceEpoch}",
      quality: 100,
    );
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Gambar berhasil disimpan")),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("ClearCut Background Remover")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (_image != null)
              Image.file(_image!, height: 200),
            ElevatedButton(onPressed: pickImage, child: const Text("Pilih Gambar")),
            ElevatedButton(onPressed: _loading ? null : removeBg, child: const Text("Remove Background")),
            if (_loading) const Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
            if (_result != null) ...[
              const SizedBox(height: 20),
              Image.memory(_result!, height: 250),
              ElevatedButton(onPressed: saveImage, child: const Text("Simpan Hasil")),
            ]
          ],
        ),
      ),
    );
  }
}
