<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PresenceChannel;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;
use App\Models\CommunityMessage; 

class MessageEvent implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    /**
     * Create a new event instance.
     */
    public $message;
    public function __construct($message)
    {
        $this->message = $message;
    }

    /**
     * Get the channels the event should broadcast on.
     *
     * @return array<int, \Illuminate\Broadcasting\Channel>
     */
    public function broadcastOn(): array
    {
        return [
            new Channel('MessageChannel'),
        ];
    }

    public function broadcastWith(): array
    {
        $replyMessage = null;

        if ($this->message->replyMessage) {
            $reply = $this->message->replyMessage;
            $replyMessage = [
                'id' => $reply->id,
                'deleted' => $reply->deleted,
                'message' => $reply->message,
                'image' => $reply->image,
                'user' => [
                    'id' => $reply->user->id,
                    'name' => $reply->user->name,
                ],
            ];
        }
        return [
            'message' => [
                'id' => $this->message->id,
                'user_id' => $this->message->user_id,
                'message' => $this->message->message,
                'image' => $this->message->image,
                'community_id' => $this->message->community_id,
                'time' => $this->message->time,
                'deleted' => $this->message->deleted,
                'reply_to' => $this->message->reply_to,
                'replyMessage' => $replyMessage,
                'user' => [
                    'id' => $this->message->user->id,
                    'name' => $this->message->user->name,
                    'type' => $this->message->user->type,
                ],
            ],
        ];
    }
}