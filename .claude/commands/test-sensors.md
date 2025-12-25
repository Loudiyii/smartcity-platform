Test IoT sensor simulation:

1. Verify API endpoint is accessible
2. Run simulation with 3 sensors in fast mode (1-minute intervals)
3. Check data is being received in database
4. Validate data ranges (PM2.5, PM10, temperature, humidity)
5. Monitor for errors or connection issues

Use `python backend/app/simulators/run_simulation.py --interval 60` for testing.
