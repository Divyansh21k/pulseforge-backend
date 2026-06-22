import React, { useState, useRef, MouseEvent } from 'react';

interface TiltCardProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
  key?: any;
}

export default function TiltCard({ children, className = '', id }: TiltCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [shineStyle, setShineStyle] = useState<React.CSSProperties>({
    opacity: 0,
  });

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current;
    if (!card) return;

    const rect = card.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    // Mouse coordinates relative to the card top-left corner
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Convert mouse coordinates to angular rotation values (-15 to +15 deg)
    const rotateYVal = ((mouseX - width / 2) / (width / 2)) * 12; // tilt left/right
    const rotateXVal = -((mouseY - height / 2) / (height / 2)) * 12; // tilt up/down

    setRotateX(rotateXVal);
    setRotateY(rotateYVal);

    // Dynamic glossy shine position
    setShineStyle({
      opacity: 0.2,
      background: `radial-gradient(circle at ${mouseX}px ${mouseY}px, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0) 60%)`,
    });
  };

  const handleMouseLeave = () => {
    // Smooth reset to neutral position
    setRotateX(0);
    setRotateY(0);
    setShineStyle({
      opacity: 0,
      transition: 'all 0.5s ease',
    });
  };

  return (
    <div
      id={id}
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`relative transition-transform duration-200 ease-out preserve-3d will-change-transform ${className}`}
      style={{
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`,
      }}
    >
      {/* Glossy light glow reflecting on the card */}
      <div
        className="absolute inset-0 pointer-events-none rounded-2xl z-10"
        style={shineStyle}
      />
      {children}
    </div>
  );
}
