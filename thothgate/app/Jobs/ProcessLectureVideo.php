<?php

namespace App\Jobs;

use App\Models\Lecture;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use ProtoneMedia\LaravelFFMpeg\Support\FFMpeg;
use FFMpeg\Format\Video\X264;

class ProcessLectureVideo implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $lecture;

    /**
     * Create a new job instance.
     */
    public function __construct(Lecture $lecture)
    {
        $this->lecture = $lecture;
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        // Mark as processing
        $this->lecture->processing_status = 'processing';
        $this->lecture->save();

        try {
            $cleanedPath = str_replace('/storage/', '', $this->lecture->video);
            $baseName = pathinfo($cleanedPath, PATHINFO_FILENAME);

            $lowBitrate = (new X264)->setKiloBitrate(500);
            $midBitrate = (new X264)->setKiloBitrate(1500);

            FFMpeg::fromDisk('public')
                ->open($cleanedPath)
                ->exportForHLS()
                ->addFormat($lowBitrate, function ($media) {
                    $media->scale(854, 480);
                })
                ->addFormat($midBitrate, function ($media) {
                    $media->scale(1280, 720);
                })
                ->onProgress(function ($percentage) {
                    // Could broadcast percentage here via websockets if desired
                })
                ->toDisk('public')
                ->save("lectures/{$baseName}/playlist.m3u8");

            // Delete original raw MP4 file to save space (optional, but good practice).
            \Illuminate\Support\Facades\Storage::disk('public')->delete($cleanedPath);

            // Update lecture to point to the new playlist
            $this->lecture->video = "/storage/lectures/{$baseName}/playlist.m3u8";
            $this->lecture->processing_status = 'completed';
            $this->lecture->save();

        } catch (\Exception $e) {
            \Illuminate\Support\Facades\Log::error("Video processing failed: " . $e->getMessage());
            
            $this->lecture->processing_status = 'failed';
            $this->lecture->save();
        }
    }
}
