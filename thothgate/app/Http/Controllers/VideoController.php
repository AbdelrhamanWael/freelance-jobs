<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class VideoController extends Controller
{
    public function streamVideo($filename)
    {
        $path = storage_path('app/public/lectures/' . $filename);

        if (!file_exists($path)) {
            abort(404);
        }

        $size = filesize($path);
        $length = $size;
        $start = 0;
        $end = $size - 1;
        $headers = [
            'Content-Type' => 'video/mp4',
            'Accept-Ranges' => 'bytes',
        ];

        if (isset($_SERVER['HTTP_RANGE'])) {
            preg_match('/bytes=(\d+)-(\d*)/', $_SERVER['HTTP_RANGE'], $matches);
            $start = intval($matches[1]);
            if (!empty($matches[2])) {
                $end = intval($matches[2]);
            }
            $length = $end - $start + 1;
            $headers['Content-Range'] = "bytes $start-$end/$size";
            $headers['Content-Length'] = $length;

            $status = 206; // Partial Content
        } else {
            $headers['Content-Length'] = $size;
            $status = 200; // OK
        }

        $stream = fopen($path, 'rb');
        fseek($stream, $start);

        return response()->stream(function () use ($stream, $length) {
            $buffer = 1024 * 8;
            $bytes = 0;
            while (!feof($stream) && $bytes < $length) {
                $read = min($buffer, $length - $bytes);
                echo fread($stream, $read);
                $bytes += $read;
                flush();
            }
            fclose($stream);
        }, $status, $headers);
    }
}
