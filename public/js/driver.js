/**
 * Easy Engineer - Driver Client
 * Handles WebSocket connection to send telemetry and pit strategy updates
 */

class DriverClient {
  constructor(sessionCode, password) {
    this.sessionCode = sessionCode;
    this.password = password;
    this.ws = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 2000;
  }

  connect() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.ws = new WebSocket(`${protocol}//${location.host}/ws/driver`);

    this.ws.onopen = () => {
      console.log('Driver connected to Easy Engineer');
      this.connected = true;
      this.reconnectAttempts = 0;
      if (this.onConnected) this.onConnected();
    };

    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === 'session:created') {
        console.log('Session created:', msg.code, msg.password);
        if (this.onSessionCreated) {
          this.onSessionCreated(msg.code, msg.password);
        }
      }

      if (msg.type === 'pit:update') {
        console.log('Pit strategy update received:', msg.data);
        if (this.onPitUpdate) {
          this.onPitUpdate(msg.data);
        }
      }
    };

    this.ws.onclose = () => {
      this.connected = false;
      console.log('Driver disconnected');
      if (this.onDisconnected) this.onDisconnected();

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting in ${this.reconnectDelay}ms...`);
        setTimeout(() => this.connect(), this.reconnectDelay);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (this.onError) this.onError(error);
    };
  }

  /**
   * Send telemetry data to the server
   * @param {Object} data - Telemetry data object
   */
  sendTelemetry(data) {
    if (!this.connected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return;
    }

    this.ws.send(JSON.stringify({
      type: 'telemetry',
      data: data
    }));
  }

  /**
   * Send pit stop strategy update from driver
   * @param {Object} pitData - Pit strategy object
   */
  sendPitUpdate(pitData) {
    if (!this.connected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return;
    }

    this.ws.send(JSON.stringify({
      type: 'pit:update',
      data: pitData
    }));
  }

  /**
   * Send complete pit stop data
   */
  sendPitStop(fuel = 0, tireCompound = 'Medium', changeTires = false, repairBody = false, repairEngine = false) {
    const pitData = {
      fuel,
      tireCompound,
      changeTires,
      repairBody,
      repairEngine
    };
    this.sendPitUpdate(pitData);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Export for use in applications
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DriverClient;
}
