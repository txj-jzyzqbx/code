<?php
// 禁止将 PHP 错误以 HTML 输出到响应
ini_set('display_errors', '0');
error_reporting(E_ALL);

// 强制 JSON 输出与 CORS 基本支持
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

ob_start(); // 捕获任何意外输出

// 捕获未处理的异常，确保返回 JSON
set_exception_handler(function($e){
    if (ob_get_length()) { ob_end_clean(); }
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Server exception: ' . $e->getMessage()], JSON_UNESCAPED_SLASHES);
    exit;
});

// 捕获致命错误（shutdown）
register_shutdown_function(function(){
    $err = error_get_last();
    if ($err && ($err['type'] & (E_ERROR | E_PARSE | E_CORE_ERROR | E_COMPILE_ERROR))) {
        if (ob_get_length()) { ob_end_clean(); }
        http_response_code(500);
        $message = "Fatal error: {$err['message']} on line {$err['line']} in {$err['file']}";
        echo json_encode(['success' => false, 'message' => $message], JSON_UNESCAPED_SLASHES);
        exit;
    }
});

try {
    // 处理 OPTIONS 预检
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        ob_end_clean();
        echo json_encode(['success' => true, 'message' => 'OK'], JSON_UNESCAPED_SLASHES);
        exit;
    }

    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        throw new Exception('只支持 POST 请求');
    }

    if (!isset($_FILES['file'])) {
        throw new Exception('未找到上传的文件（字段名应为 "file"）');
    }

    // 配置
    $uploadDir = 'images';
    $maxFileSize = 10 * 1024 * 1024; // 10MB
    $allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    $allowedExtensions = ['jpg','jpeg','png','webp','gif'];

    // 确保目录存在并可写
    if (!is_dir($uploadDir)) {
        if (!mkdir($uploadDir, 0755, true)) {
            throw new Exception('无法创建上传目录: ' . $uploadDir);
        }
    }
    if (!is_writable($uploadDir)) {
        throw new Exception('上传目录不可写: ' . realpath($uploadDir));
    }

    $file = $_FILES['file'];

    // 上传错误检查
    if ($file['error'] !== UPLOAD_ERR_OK) {
        $errorMessages = [
            UPLOAD_ERR_INI_SIZE => '文件大小超过服务器限制',
            UPLOAD_ERR_FORM_SIZE => '文件大小超过表单限制',
            UPLOAD_ERR_PARTIAL => '文件上传不完整',
            UPLOAD_ERR_NO_FILE => '未选择文件',
            UPLOAD_ERR_NO_TMP_DIR => '服务器临时目录错误',
            UPLOAD_ERR_CANT_WRITE => '无法写入文件',
            UPLOAD_ERR_EXTENSION => '文件上传被扩展停止'
        ];
        throw new Exception($errorMessages[$file['error']] ?? '未知上传错误');
    }

    if ($file['size'] > $maxFileSize) {
        throw new Exception('文件大小超过限制（最大 ' . ($maxFileSize / 1024 / 1024) . 'MB）');
    }

    // MIME 类型检测（优先 fileinfo；后备 getimagesize；最后使用客户端类型）
    $mimeType = null;

    if (function_exists('finfo_open')) {
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        if ($finfo !== false) {
            $detected = finfo_file($finfo, $file['tmp_name']);
            finfo_close($finfo);
            if ($detected) { $mimeType = $detected; }
        }
    }

    if (empty($mimeType) && function_exists('getimagesize')) {
        $imgInfo = @getimagesize($file['tmp_name']);
        if ($imgInfo && !empty($imgInfo['mime'])) {
            $mimeType = $imgInfo['mime'];
        }
    }

    if (empty($mimeType)) {
        $mimeType = !empty($file['type']) ? $file['type'] : 'application/octet-stream';
    }

    if (!in_array($mimeType, $allowedTypes)) {
        throw new Exception('不支持的文件类型: ' . $mimeType);
    }

    $fileExtension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($fileExtension, $allowedExtensions)) {
        throw new Exception('不支持的文件扩展名: ' . $fileExtension);
    }

    // 生成唯一文件名并移动
    $newFileName = time() . '_' . bin2hex(random_bytes(8)) . '.' . $fileExtension;
    $destPath = rtrim($uploadDir, '/\\') . '/' . $newFileName;

    if (!move_uploaded_file($file['tmp_name'], $destPath)) {
        throw new Exception('文件保存失败 (move_uploaded_file 返回 false)');
    }

    // 生成可访问 URL (规范化斜杠)
    $protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (isset($_SERVER['SERVER_PORT']) && $_SERVER['SERVER_PORT'] == 443) ? 'https://' : 'http://';
    $host = $_SERVER['HTTP_HOST'] ?? ($_SERVER['SERVER_NAME'] ?? '');
    $scriptDir = dirname($_SERVER['SCRIPT_NAME'] ?? '');
    $scriptDir = ($scriptDir === '/' || $scriptDir === '\\') ? '' : rtrim($scriptDir, '/\\');
    $normalized = str_replace('\\', '/', $destPath);
    $fileUrl = $protocol . $host . ($scriptDir ? '/' . ltrim($scriptDir, '/') : '') . '/' . ltrim($normalized, '/');

    // 丢弃缓冲中的任意输出，返回 JSON
    ob_end_clean();
    echo json_encode([
        'success' => true,
        'message' => '文件上传成功',
        'url' => $fileUrl,
        'fileName' => $newFileName,
        'fileSize' => $file['size']
    ], JSON_UNESCAPED_SLASHES);

} catch (Exception $e) {
    if (ob_get_length()) { ob_end_clean(); }
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => $e->getMessage()], JSON_UNESCAPED_SLASHES);
}