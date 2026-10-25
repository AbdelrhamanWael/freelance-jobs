"use client";

import { motion } from "framer-motion";
import { type LucideIcon } from "lucide-react";

interface AnimatedIconProps {
  icon: LucideIcon;
  size?: number;
  className?: string;
}

export default function AnimatedIcon({ icon: Icon, size = 24, className = "" }: AnimatedIconProps) {
  return (
    <motion.div
      className={`relative flex items-center justify-center text-[#044a49] ${className}`}
      whileHover={{ scale: 1.1, rotate: -5 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 10 }}
    >
      <Icon 
        size={size} 
        strokeWidth={1.5}
        className="stroke-current"
      />
    </motion.div>
  );
}
