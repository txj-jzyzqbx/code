<?php
// translate.php - 服务器代理：用服务器端 USER_KEY 生成 Sign 并转发到第三方图片翻译 API
// IMPORTANT: 把 $USER_KEY 改为你在第三方控制台的用户密钥，并在生产环境做好鉴权/访问限制。
// 放到 d:\phpstudy_pro\WWW\test\translate.php

ini_set('display_errors', 0);
header('Content-Type: application/json; charset=utf-8');

// 在此处设置你的服务器端保密 UserKey（不要把这个文件公开到未经授权访问）
$USER_KEY = '2882872013';
$TRANS_KEY = '1768209419';

// 简单允许只来自同源的请求（如果你需要跨域，请按需放开）
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'method_not_allowed']);
    exit;
}

// 读取前端发来的 JSON
$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) {
    http_response_code(400);
    echo json_encode(['error' => 'invalid_json']);
    exit;
}

$imageUrls = $input['imageUrls'] ?? null;
$imgTransKey = $input['imgTransKey'] ?? null;
$sourceLanguage = $input['sourceLanguage'] ?? 'CHS';
$targetLanguage = $input['targetLanguage'] ?? 'ENG';
$syncMode = $input['syncMode'] ?? '1';
$qos = $input['qos'] ?? 'LowLatency';
$engineType = $input['engineType'] ?? null;
$needWatermark = isset($input['needWatermark']) ? ($input['needWatermark'] ? '1' : '0') : null;
$needRmUrl = isset($input['needRmUrl']) ? ($input['needRmUrl'] ? '1' : '0') : null;

// Basic validation
if (empty($imageUrls) || !is_array($imageUrls) || empty($imgTransKey)) {
    http_response_code(400);
    echo json_encode(['error' => 'missing_parameters']);
    exit;
}

// CommitTime 必须为秒
$commitTime = time();
$sign = strtolower(md5($commitTime . '_' . $USER_KEY . '_' . $TRANS_KEY));

// API 要求：每个 URL urlencode，然后用英文逗号拼接
$encoded = array_map('urlencode', $imageUrls);
$urlsJoined = implode(',', $encoded);

// 准备 POST 字段
$post = [
    'Action' => 'GetImageTranslateBatch',
    'SourceLanguage' => $sourceLanguage,
    'TargetLanguage' => $targetLanguage,
    'Urls' => $urlsJoined,
    'ImgTransKey' => $imgTransKey,
    'CommitTime' => (string)$commitTime,
    'Sign' => $sign,
    'Sync' => (string)$syncMode,
    'Qos' => $qos,
];

if (!empty($engineType)) $post['EngineType'] = $engineType;
if ($needWatermark !== null) $post['NeedWatermark'] = $needWatermark;
if ($needRmUrl !== null) $post['NeedRmUrl'] = $needRmUrl;

// 发起到第三方 API 的请求
$ch = curl_init('https://api.tosoiot.com');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($post));
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

// 可选：如果你在本地开发需要忽略 SSL 验证，请小心使用；生产环境不建议禁用
// curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlErr = curl_error($ch);
curl_close($ch);

if ($response === false) {
    http_response_code(502);
    echo json_encode(['error' => 'upstream_error', 'detail' => $curlErr]);
    exit;
}

// 直接返回第三方 API 的原始响应（通常为 JSON）
http_response_code($httpCode ?: 200);
echo $response;