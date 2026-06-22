import React from 'react';

export default function AmbientBackgroundDecoration() {
  return (
    <div 
      className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none select-none z-0"
      id="ambient-background-decoration"
    >
      {/* Soft blurred ambient luxury light glows */}
      <div 
        className="absolute w-[45vw] h-[45vw] rounded-full blur-[120px] opacity-[0.22] mix-blend-multiply animate-pulse"
        style={{
          background: 'radial-gradient(circle, rgba(196, 180, 149, 0.6) 0%, rgba(218, 207, 188, 0) 70%)',
          top: '-10%',
          right: '-5%',
          animationDuration: '24s'
        }}
      />
      <div 
        className="absolute w-[50vw] h-[50vw] rounded-full blur-[140px] opacity-[0.14] mix-blend-multiply animate-pulse"
        style={{
          background: 'radial-gradient(circle, rgba(11, 30, 54, 0.4) 0%, rgba(11, 30, 54, 0) 75%)',
          bottom: '10%',
          left: '-10%',
          animationDuration: '32s'
        }}
      />
      <div 
        className="absolute w-[35vw] h-[35vw] rounded-full blur-[100px] opacity-[0.18] mix-blend-multiply animate-pulse"
        style={{
          background: 'radial-gradient(circle, rgba(196, 180, 149, 0.45) 0%, rgba(196, 180, 149, 0) 70%)',
          top: '40%',
          left: '35%',
          animationDuration: '20s'
        }}
      />

      {/* Subtle vector grid and connection points floating decoration */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.04]" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="chess-grid" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="#0B1E36" strokeWidth="1" />
            <circle cx="0" cy="0" r="2.5" fill="#C4B495" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#chess-grid)" />
      </svg>

      {/* Elegantly floating geometric node paths */}
      <div className="absolute inset-0 w-full h-full opacity-[0.06]">
        <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" preserveAspectRatio="none">
          <path 
            d="M -100,200 C 300,100 500,400 900,250 C 1200,150 1300,500 1600,450" 
            fill="none" 
            stroke="#C4B495" 
            strokeWidth="1.5" 
            strokeDasharray="5,10"
          />
          <path 
            d="M -50,600 C 400,750 700,500 1000,700 C 1200,800 1350,600 1550,650" 
            fill="none" 
            stroke="#0B1E36" 
            strokeWidth="1.5" 
            strokeDasharray="4,8"
          />
          
          {/* Animated floating node points key accents */}
          <circle cx="300" cy="100" r="3" fill="#C4B495" className="animate-ping" style={{ animationDuration: '4s' }} />
          <circle cx="900" cy="250" r="4" fill="#0B1E36" />
          <circle cx="1000" cy="700" r="3" fill="#C4B495" />
        </svg>
      </div>
    </div>
  );
}
