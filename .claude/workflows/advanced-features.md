# Workflow: Advanced Features

## Objectif
Ajouter carte interactive multi-couches et features avancées dashboard.

## Référence
- **User Stories:** US-012, US-013, US-014
- **Skills:** `frontend-dashboard`, `backend-api`

## Étapes

### 1. Interactive Map (5 layers)
```typescript
// frontend/src/components/Map/MultiLayerMap.tsx
<MapContainer>
  <LayersControl>
    <Overlay name="IoT Sensors">
      <IoTSensorsLayer />
    </Overlay>
    <Overlay name="Vélib Stations">
      <VelibStationsLayer />
    </Overlay>
    <Overlay name="Air Quality Heatmap">
      <HeatmapLayer />
    </Overlay>
  </LayersControl>
</MapContainer>
```

### 2. Correlation Charts
```typescript
// Pollution + Weather correlation
<Line data={{
  datasets: [
    { label: 'PM2.5', data: pm25Data },
    { label: 'Temperature', data: tempData, yAxisID: 'y2' }
  ]
}} />
```

### 3. Data Export
```python
@router.get("/export/csv")
async def export_csv():
    data = await get_air_quality_history()
    df = pd.DataFrame(data)
    return df.to_csv()
```

## Critères
- [ ] Map 5 layers fonctionnelles
- [ ] Correlation charts affichés
- [ ] Export CSV/PDF
