import React from 'react';
import { motion } from 'motion/react';

interface ScrollRevealProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  y?: number;
  className?: string;
}

export default function ScrollReveal({
  children,
  delay = 0,
  duration = 1.1,
  y = 25,
  className = '',
}: ScrollRevealProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ delay, duration, ease: [0.16, 1, 0.3, 1] }} // elegant cubic-bezier out ease
      className={className}
    >
      {children}
    </motion.div>
  );
}
