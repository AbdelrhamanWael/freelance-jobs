<style>
    .pagination {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        /* flex-direction: column; */
    }
</style>
@if ($paginator->hasPages())
    <div class="pagination">
        {{-- Page Numbers --}}
        
        @if (!$paginator->onFirstPage())
            <a href="{{ $paginator->previousPageUrl() }}" class="btn">Previous</a>
        @endif            
        <span class="page-numbers">
            @foreach ($elements as $element)
                {{-- "Three Dots" Separator --}}
                @if (is_string($element))
                    <span class="mx-1">{{ $element }}</span>
                @endif

                @if (is_array($element))
                    @foreach ($element as $page => $url)
                        @if ($page > 1)
                            <span> | </span>
                        @endif
                        <a href="{{ $url }}" class="mx-1" style="text-decoration: none; color:{{ $page == $paginator->currentPage() ? '#d4af37' : 'white' }}">{{ $page }}</a>
                    @endforeach
                @endif
            @endforeach
        </span>
        @if ($paginator->hasMorePages())
            <a href="{{ $paginator->nextPageUrl() }}" class="btn">Next</a>
        @endif
    </div>
@endif
