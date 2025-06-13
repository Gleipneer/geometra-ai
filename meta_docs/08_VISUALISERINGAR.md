# Implementera Visualiseringar

Detta dokument beskriver hur man implementerar geometriska visualiseringar i Geometra AI-systemet.

## Översikt

Visualiseringssystemet hanterar:

1. **2D-visualiseringar**
   - Grundläggande former
   - Transformationer
   - Mätningar

2. **3D-visualiseringar**
   - Volymberäkningar
   - Perspektiv
   - Rotation

3. **Interaktiva element**
   - Zoom
   - Pan
   - Mätverktyg

## Installation

1. Installera beroenden:
```bash
pnpm install three @react-three/fiber @react-three/drei
pnpm install d3
pnpm install mathjs
```

2. Skapa visualiseringsstruktur:
```bash
mkdir -p src/visualizations/{2d,3d,utils}
```

## Konfiguration

### 2D-visualiseringar

1. Skapa `src/visualizations/2d/GeometryRenderer.tsx`:
```typescript
"""2D geometry renderer component."""

import React, { useRef, useEffect } from 'react';
import { Box } from '@mui/material';
import { GeometryObject, Point, Line, Circle, Rectangle } from '@/types/geometry';
import { useGeometryContext } from '@/contexts/GeometryContext';

interface GeometryRendererProps {
  width?: number;
  height?: number;
  scale?: number;
}

export const GeometryRenderer: React.FC<GeometryRendererProps> = ({
  width = 800,
  height = 600,
  scale = 1
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { objects, selectedObject, setSelectedObject } = useGeometryContext();
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Rensa canvas
    ctx.clearRect(0, 0, width, height);
    
    // Rita rutnät
    drawGrid(ctx, width, height, scale);
    
    // Rita objekt
    objects.forEach(obj => {
      switch (obj.type) {
        case 'point':
          drawPoint(ctx, obj, scale);
          break;
        case 'line':
          drawLine(ctx, obj, scale);
          break;
        case 'circle':
          drawCircle(ctx, obj, scale);
          break;
        case 'rectangle':
          drawRectangle(ctx, obj, scale);
          break;
      }
    });
    
    // Rita mätningar
    drawMeasurements(ctx, objects, scale);
  }, [objects, selectedObject, width, height, scale]);
  
  const drawGrid = (
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    scale: number
  ) => {
    const gridSize = 50 * scale;
    
    ctx.beginPath();
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 0.5;
    
    // Rita vertikala linjer
    for (let x = 0; x <= width; x += gridSize) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
    }
    
    // Rita horisontella linjer
    for (let y = 0; y <= height; y += gridSize) {
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
    }
    
    ctx.stroke();
  };
  
  const drawPoint = (
    ctx: CanvasRenderingContext2D,
    point: Point,
    scale: number
  ) => {
    const { x, y } = point;
    
    ctx.beginPath();
    ctx.arc(x * scale, y * scale, 4, 0, 2 * Math.PI);
    ctx.fillStyle = point === selectedObject ? '#f00' : '#000';
    ctx.fill();
  };
  
  const drawLine = (
    ctx: CanvasRenderingContext2D,
    line: Line,
    scale: number
  ) => {
    const { x1, y1, x2, y2 } = line;
    
    ctx.beginPath();
    ctx.moveTo(x1 * scale, y1 * scale);
    ctx.lineTo(x2 * scale, y2 * scale);
    ctx.strokeStyle = line === selectedObject ? '#f00' : '#000';
    ctx.lineWidth = 2;
    ctx.stroke();
  };
  
  const drawCircle = (
    ctx: CanvasRenderingContext2D,
    circle: Circle,
    scale: number
  ) => {
    const { x, y, radius } = circle;
    
    ctx.beginPath();
    ctx.arc(x * scale, y * scale, radius * scale, 0, 2 * Math.PI);
    ctx.strokeStyle = circle === selectedObject ? '#f00' : '#000';
    ctx.lineWidth = 2;
    ctx.stroke();
  };
  
  const drawRectangle = (
    ctx: CanvasRenderingContext2D,
    rect: Rectangle,
    scale: number
  ) => {
    const { x, y, width, height } = rect;
    
    ctx.beginPath();
    ctx.rect(
      x * scale,
      y * scale,
      width * scale,
      height * scale
    );
    ctx.strokeStyle = rect === selectedObject ? '#f00' : '#000';
    ctx.lineWidth = 2;
    ctx.stroke();
  };
  
  const drawMeasurements = (
    ctx: CanvasRenderingContext2D,
    objects: GeometryObject[],
    scale: number
  ) => {
    objects.forEach(obj => {
      switch (obj.type) {
        case 'line':
          drawLineMeasurement(ctx, obj, scale);
          break;
        case 'circle':
          drawCircleMeasurement(ctx, obj, scale);
          break;
        case 'rectangle':
          drawRectangleMeasurement(ctx, obj, scale);
          break;
      }
    });
  };
  
  return (
    <Box
      sx={{
        width,
        height,
        border: '1px solid',
        borderColor: 'divider',
        position: 'relative'
      }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{ cursor: 'crosshair' }}
      />
    </Box>
  );
};
```

### 3D-visualiseringar

1. Skapa `src/visualizations/3d/Scene3D.tsx`:
```typescript
"""3D scene component."""

import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { Box, Cylinder, Sphere } from '@/types/geometry3d';

interface Scene3DProps {
  objects: (Box | Cylinder | Sphere)[];
  width?: number;
  height?: number;
}

export const Scene3D: React.FC<Scene3DProps> = ({
  objects,
  width = 800,
  height = 600
}) => {
  return (
    <Canvas
      camera={{ position: [5, 5, 5], fov: 75 }}
      style={{ width, height }}
    >
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      
      <Grid
        args={[10, 10]}
        position={[0, 0, 0]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#6f6f6f"
        sectionSize={1}
        sectionThickness={1}
        sectionColor="#9d4b4b"
        fadeDistance={30}
        fadeStrength={1}
        followCamera={false}
        infiniteGrid={true}
      />
      
      {objects.map((obj, index) => {
        switch (obj.type) {
          case 'box':
            return (
              <mesh
                key={index}
                position={[obj.x, obj.y, obj.z]}
                rotation={[obj.rotationX, obj.rotationY, obj.rotationZ]}
              >
                <boxGeometry
                  args={[obj.width, obj.height, obj.depth]}
                />
                <meshStandardMaterial color={obj.color} />
              </mesh>
            );
          case 'cylinder':
            return (
              <mesh
                key={index}
                position={[obj.x, obj.y, obj.z]}
                rotation={[obj.rotationX, obj.rotationY, obj.rotationZ]}
              >
                <cylinderGeometry
                  args={[obj.radius, obj.radius, obj.height, 32]}
                />
                <meshStandardMaterial color={obj.color} />
              </mesh>
            );
          case 'sphere':
            return (
              <mesh
                key={index}
                position={[obj.x, obj.y, obj.z]}
              >
                <sphereGeometry args={[obj.radius, 32, 32]} />
                <meshStandardMaterial color={obj.color} />
              </mesh>
            );
        }
      })}
      
      <OrbitControls />
    </Canvas>
  );
};
```

### Visualiseringsverktyg

1. Skapa `src/visualizations/utils/transformations.ts`:
```typescript
"""Geometry transformation utilities."""

import { Point, Line, Circle, Rectangle } from '@/types/geometry';
import { Matrix } from 'mathjs';

export const rotate = (
  point: Point,
  center: Point,
  angle: number
): Point => {
  const radians = (angle * Math.PI) / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);
  
  const dx = point.x - center.x;
  const dy = point.y - center.y;
  
  return {
    x: center.x + dx * cos - dy * sin,
    y: center.y + dx * sin + dy * cos
  };
};

export const scale = (
  point: Point,
  center: Point,
  factor: number
): Point => {
  return {
    x: center.x + (point.x - center.x) * factor,
    y: center.y + (point.y - center.y) * factor
  };
};

export const translate = (
  point: Point,
  dx: number,
  dy: number
): Point => {
  return {
    x: point.x + dx,
    y: point.y + dy
  };
};

export const applyTransformation = (
  object: Point | Line | Circle | Rectangle,
  matrix: Matrix
): Point | Line | Circle | Rectangle => {
  switch (object.type) {
    case 'point':
      return {
        ...object,
        x: matrix.get([0, 0]) * object.x + matrix.get([0, 1]) * object.y + matrix.get([0, 2]),
        y: matrix.get([1, 0]) * object.x + matrix.get([1, 1]) * object.y + matrix.get([1, 2])
      };
    case 'line':
      return {
        ...object,
        x1: matrix.get([0, 0]) * object.x1 + matrix.get([0, 1]) * object.y1 + matrix.get([0, 2]),
        y1: matrix.get([1, 0]) * object.x1 + matrix.get([1, 1]) * object.y1 + matrix.get([1, 2]),
        x2: matrix.get([0, 0]) * object.x2 + matrix.get([0, 1]) * object.y2 + matrix.get([0, 2]),
        y2: matrix.get([1, 0]) * object.x2 + matrix.get([1, 1]) * object.y2 + matrix.get([1, 2])
      };
    case 'circle':
      return {
        ...object,
        x: matrix.get([0, 0]) * object.x + matrix.get([0, 1]) * object.y + matrix.get([0, 2]),
        y: matrix.get([1, 0]) * object.x + matrix.get([1, 1]) * object.y + matrix.get([1, 2]),
        radius: object.radius * Math.sqrt(
          matrix.get([0, 0]) * matrix.get([0, 0]) +
          matrix.get([0, 1]) * matrix.get([0, 1])
        )
      };
    case 'rectangle':
      return {
        ...object,
        x: matrix.get([0, 0]) * object.x + matrix.get([0, 1]) * object.y + matrix.get([0, 2]),
        y: matrix.get([1, 0]) * object.x + matrix.get([1, 1]) * object.y + matrix.get([1, 2]),
        width: object.width * Math.sqrt(
          matrix.get([0, 0]) * matrix.get([0, 0]) +
          matrix.get([0, 1]) * matrix.get([0, 1])
        ),
        height: object.height * Math.sqrt(
          matrix.get([1, 0]) * matrix.get([1, 0]) +
          matrix.get([1, 1]) * matrix.get([1, 1])
        )
      };
  }
};
```

## Validering

1. Testa 2D-visualiseringar:
```typescript
import { GeometryRenderer } from '@/visualizations/2d/GeometryRenderer';

const objects = [
  {
    type: 'circle',
    x: 100,
    y: 100,
    radius: 50
  },
  {
    type: 'rectangle',
    x: 200,
    y: 200,
    width: 100,
    height: 50
  }
];

<GeometryRenderer objects={objects} />
```

2. Testa 3D-visualiseringar:
```typescript
import { Scene3D } from '@/visualizations/3d/Scene3D';

const objects = [
  {
    type: 'box',
    x: 0,
    y: 0,
    z: 0,
    width: 1,
    height: 1,
    depth: 1,
    color: '#ff0000'
  },
  {
    type: 'sphere',
    x: 2,
    y: 0,
    z: 0,
    radius: 0.5,
    color: '#00ff00'
  }
];

<Scene3D objects={objects} />
```

3. Kör visualiseringstester:
```bash
pnpm test visualizations
```

## Felsökning

### Visualiseringsproblem

1. **Rendering-problem**
   - Kontrollera canvas-kontext
   - Verifiera koordinatsystem
   - Validera transformationer

2. **Prestandaproblem**
   - Optimera rendering
   - Implementera caching
   - Validera minnesanvändning

3. **Interaktionsproblem**
   - Kontrollera event-hantering
   - Verifiera zoom/pan
   - Validera mätverktyg

## Loggning

1. Konfigurera loggning i `src/visualizations/utils/logging.ts`:
```typescript
"""Visualization logging configuration."""

import { createLogger, format, transports } from 'winston';

const logger = createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  transports: [
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.simple()
      )
    }),
    new transports.File({
      filename: 'logs/visualizations.log'
    })
  ]
});

export default logger;
```

## Nästa steg

1. Konfigurera [Deployment](09_DEPLOYMENT.md)
2. Skapa [Dokumentation](10_DOKUMENTATION.md)
3. Implementera [Tester](11_TESTER.md) 