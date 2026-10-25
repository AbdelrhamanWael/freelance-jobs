/**
 * Sidebar.jsx
 * ───────────────────────────────────────────────────────────────
 * History panel — slides in from the right.
 * Shows previously generated models with mini-icons.
 */

import React from 'react';
import { X, Clock, Download, Box, Circle, RotateCw, Gem, Cone, ChevronLeft } from 'lucide-react';

const SHAPE_ICONS = {
  box:         <Box size={16} />,
  sphere:      <Circle size={16} />,
  torus:       <RotateCw size={16} />,
  icosahedron: <Gem size={16} />,
  cone:        <Cone size={16} />,
};

const HISTORY = [
  { id: 1, title: 'كرسي مكتبي عصري', date: 'قبل ساعتين', shape: 'box',         tag: 'Geometric' },
  { id: 2, title: 'مصباح كروي ناعم',  date: 'أمس',        shape: 'sphere',      tag: 'Organic'   },
  { id: 3, title: 'هيكل بلوري',       date: 'قبل 3 أيام', shape: 'icosahedron', tag: 'Crystal'   },
  { id: 4, title: 'إطار دائري',       date: 'قبل أسبوع',  shape: 'torus',       tag: 'Flow'      },
];

const TAG_COLORS = {
  Geometric: '#7C3AED',
  Organic:   '#6366F1',
  Crystal:   '#00D4FF',
  Flow:      '#EC4899',
};

export default function Sidebar({ isOpen, onClose, onSelectHistory }) {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Panel */}
      <div
        className={`
          fixed top-0 right-0 h-full w-80 z-[70]
          flex flex-col
          bg-[#080809] border-r border-white/8
          transform transition-transform duration-300
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
        style={{ backdropFilter: 'blur(24px)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-white/8">
          <div className="flex items-center gap-2.5">
            <Clock size={18} className="text-primary" />
            <h2 className="font-bold text-white">سجل النماذج</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-white/5 hover:bg-white/12 border border-white/8 flex items-center justify-center text-muted-foreground hover:text-white transition-all cursor-pointer"
          >
            <X size={16} />
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {HISTORY.map((item) => (
            <div
              key={item.id}
              className="group flex items-center gap-3 p-3 rounded-2xl hover:bg-white/5 border border-transparent hover:border-white/8 transition-all cursor-pointer"
              onClick={() => { onSelectHistory(item.shape); onClose(); }}
            >
              {/* Icon */}
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{
                  background: `${TAG_COLORS[item.tag]}18`,
                  border: `1px solid ${TAG_COLORS[item.tag]}30`,
                  color: TAG_COLORS[item.tag],
                }}
              >
                {SHAPE_ICONS[item.shape]}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-white group-hover:text-primary transition-colors truncate">
                  {item.title}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">{item.date}</p>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => e.stopPropagation()}
                  className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/15 flex items-center justify-center text-muted-foreground hover:text-white transition-all cursor-pointer"
                  title="تحميل"
                >
                  <Download size={13} />
                </button>
                <div className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/15 flex items-center justify-center text-muted-foreground hover:text-primary transition-all cursor-pointer"
                  title="فتح">
                  <ChevronLeft size={13} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/8">
          <p className="text-xs text-muted-foreground text-center">
            يتم حفظ النماذج لمدة <span className="text-white">30 يوماً</span>
          </p>
        </div>
      </div>
    </>
  );
}
