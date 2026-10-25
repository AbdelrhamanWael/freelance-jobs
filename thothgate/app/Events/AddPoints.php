<?php

namespace App\Events;

use App\Models\PointsHistroy;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PresenceChannel;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class AddPoints implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;
    /**
     * The reason for adding points.
     * @var PointsHistroy
     */
    public $points;

    /**
     * Create a new event instance.
     * * @param int $student_id
     * @param int $points
     * @param string $reason
     */
    public function __construct(PointsHistroy $points)
    {
        $this->points = $points;
    }

    /**
     * Get the channels the event should broadcast on.
     *
     * @return array<int, \Illuminate\Broadcasting\Channel>
     */
    public function broadcastOn(): array
    {
        return [
            new PrivateChannel('AddPoints.' . $this->points->student_id),
        ];
    }

    /**
     * The name of the event as it should be broadcast.
     *
     * @return string
     */
    public function broadcastAs(): string
    {
        return 'points.added';
    }
    public function broadcastWith(): array
    {
        return [
            'id' => $this->points->id,
            'points' => $this->points->points,
            'reason' => $this->points->reason,
            'student_id' => $this->points->student_id,
        ];
    }
}
