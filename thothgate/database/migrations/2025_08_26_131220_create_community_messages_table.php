<?php

use App\Models\Community;
use App\Models\CommunityMessage;
use App\Models\User;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('community_messages', function (Blueprint $table) {
            $table->id();
            $table->foreignIdFor(User::class)->constrained()->cascadeOnDelete();
            $table->foreignIdFor(Community::class)->constrained()->cascadeOnDelete();
            $table->foreignId('reply_to')
                ->nullable()
                ->constrained('community_messages')
                ->nullOnDelete();
            $table->index('community_id');
            $table->text('message')->nullable();
            $table->string('image')->nullable();
            $table->string('time');
            $table->boolean('deleted')->default(false);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('community_messages');
    }
};
