import React, { useEffect, useRef } from 'react';

export default function NetworkMeshCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: -1000, y: -1000, rx: -1000, ry: -1000 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // Dynamic sizing listener
    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Mouse movement listeners
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current.x = e.clientX;
      mouseRef.current.y = e.clientY;
    };
    const handleMouseLeave = () => {
      mouseRef.current.x = -1000;
      mouseRef.current.y = -1000;
    };
    window.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    // Particle class representing nodes
    class Node {
      x: number;
      y: number;
      vx: number;
      vy: number;
      radius: number;
      color: string;

      constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        // Low velocity for an elegant float
        this.vx = (Math.random() - 0.5) * 0.45;
        this.vy = (Math.random() - 0.5) * 0.45;
        this.radius = Math.random() * 2 + 1;
        this.color = Math.random() > 0.6 ? '#C4B495' : '#0076ce'; // Gold accent or Dell Blue
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        // Gravity pull to mouse if within reach
        const dx = mouseRef.current.x - this.x;
        const dy = mouseRef.current.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 180) {
          const force = (180 - dist) / 180;
          this.x += (dx / dist) * force * 0.8;
          this.y += (dy / dist) * force * 0.8;
        }

        // Boundary reflection
        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
      }

      draw(c: CanvasRenderingContext2D) {
        c.beginPath();
        c.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        c.fillStyle = this.color;
        c.fill();
      }
    }

    const nodeCount = Math.min(65, Math.floor((width * height) / 22000));
    const nodes: Node[] = [];
    for (let i = 0; i < nodeCount; i++) {
      nodes.push(new Node());
    }

    // Animation Loop
    const drawLoop = () => {
      ctx.clearRect(0, 0, width, height);

      // Smooth mouse spring interpolator
      mouseRef.current.rx += (mouseRef.current.x - mouseRef.current.rx) * 0.1;
      mouseRef.current.ry += (mouseRef.current.y - mouseRef.current.ry) * 0.1;

      // Render subtle gravitational field around mouse
      if (mouseRef.current.x > 0) {
        ctx.beginPath();
        const grad = ctx.createRadialGradient(
          mouseRef.current.rx,
          mouseRef.current.ry,
          10,
          mouseRef.current.rx,
          mouseRef.current.ry,
          150
        );
        grad.addColorStop(0, 'rgba(0, 118, 206, 0.04)');
        grad.addColorStop(1, 'rgba(0, 118, 206, 0)');
        ctx.fillStyle = grad;
        ctx.arc(mouseRef.current.rx, mouseRef.current.ry, 150, 0, Math.PI * 2);
        ctx.fill();
      }

      // Update & Draw nodes
      nodes.forEach((node) => {
        node.update();
        node.draw(ctx);
      });

      // Connect nodes dynamically
      ctx.lineWidth = 0.55;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          // Proximity threshold
          if (distance < 110) {
            const alpha = (110 - distance) / 110;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            // Mix line color based on dynamic weight
            ctx.strokeStyle = `rgba(196, 180, 149, ${alpha * 0.18})`; 
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(drawLoop);
    };

    // Begin looping
    drawLoop();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none select-none z-10 opacity-[0.75] mix-blend-screen"
      style={{ backfaceVisibility: 'hidden' }}
    />
  );
}
