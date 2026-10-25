<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Community extends Model
{
    protected $guarded = [];
    protected $table = 'communities';

    public function messages()
    {
        return $this->hasMany(CommunityMessage::class);
    }
    public function purchased_communities(){
        return $this->hasMany(PurchasedCommunity::class);
    }
}
