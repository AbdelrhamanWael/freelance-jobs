<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Monolog\Level;

class Student extends Model
{
    protected $guarded = [];
    protected $table = 'students';

    static $levels = [
        'كاتب المعبد'   => [0, 1000],
        'حامل البردية'  => [1000, 2000],
        'حارس الأسرار'  => [2000, 3000],
        'حكيم المعبد'   => [3000, 4000],
        'Thoth'         => [4000, INF],
    ];

    public static function getLevel($points)
    {
        foreach (self::$levels as $level => [$min, $max]) {
            if ($points >= $min && $points < $max) {
                return $level;
            }
        }
        return null;
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
    public function lectures()
    {
        return $this->hasMany(PurchasedLectures::class);
    }
    public function sessions()
    {
        return $this->hasMany(ExamSession::class);
    }
    public function messages()
    {
        return $this->hasMany(CommunityMessage::class);
    }
    public function pointsHistory(){
        return $this->hasMany(PointsHistroy::class);
    }
    public function packages(){
        return $this->hasMany(StudentPackage::class);
    }
}
