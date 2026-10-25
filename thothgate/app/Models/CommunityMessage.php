<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CommunityMessage extends Model
{
    protected $guarded = [];
    protected $table = 'community_messages';
    public function community()
    {
        return $this->belongsTo(Community::class);
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
    public function replyMessage()
    {
        return $this->belongsTo(CommunityMessage::class, 'reply_to');
    }

    public function replies()
    {
        return $this->hasMany(CommunityMessage::class, 'reply_to');
    }
}
