# IronBeam SDK Documentation

Welcome to the comprehensive documentation for the IronBeam Python SDK.

## 📚 Documentation Index

### Core Documentation
- **[Main README](../README.md)** - Complete SDK overview and quick start guide
- **[Installation & Setup](../README.md#installation)** - Installation instructions and requirements

### API Reference
- **[MBO Data Guide](MBO_DATA_GUIDE.md)** - Market by Order data format and usage
- **[Streaming Data Dictionary](STREAMING_DATA_DICTIONARY.md)** - WebSocket streaming data reference

### Account Management
- **[Demo Account Reset](DEMO_ACCOUNT_RESET.md)** - Guide for resetting demo trading accounts

### Development & Publishing
- **[Package Publication Summary](PACKAGE_PUBLICATION_SUMMARY.md)** - Package build and publication status
- **[Publishing Guide](PUBLISHING_GUIDE.md)** - Step-by-step guide for publishing to PyPI
- **[Bug Fix Summary](BUG_FIX_SUMMARY.md)** - Recent bug fixes and improvements

### Examples
- **[Examples Directory](../examples/)** - Complete code examples and tutorials
- **[Scripts Directory](../scripts/)** - Utility scripts for account management

## 🚀 Quick Links

### Getting Started
1. [Installation](../README.md#installation)
2. [Authentication](../README.md#quick-start)
3. [Basic Usage](../README.md#basic-usage)
4. [Auto Breakeven](../README.md#auto-breakeven)
5. [Running Take Profit](../README.md#running-take-profit)

### Advanced Features
- [WebSocket Streaming](../README.md#websocket-streaming)
- [Data Model Compatibility](../README.md#data-model-compatibility--robustness)
- [Field Name Flexibility](../README.md#field-name-flexibility)
- [Order Serialization](../README.md#order-serialization)

### Reference
- [API Coverage](../README.md#api-coverage)
- [Architecture](../README.md#architecture)
- [Configuration Examples](../README.md#configuration-examples)

## 🛠️ SDK Features

### ✅ Production Ready
- Comprehensive field name compatibility
- Robust error handling and validation
- Extensive testing with various API response formats
- Auto-reconnect and state management for streaming
- Thread-safe execution engines

### 🔧 Technical Features
- **Pydantic v2** models with AliasChoices for dual field name support
- **WebSocket streaming** with real-time market data
- **Automated trading** with auto-breakeven and running take-profit
- **Bracket orders** with proper stop-loss and take-profit serialization
- **Type safety** with comprehensive type hints

### 📊 Trading Features
- **49 API endpoints** fully implemented
- **Real-time streaming** with sub-100ms latency
- **Auto breakeven** with 3-level progressive stop-loss
- **Running take profit** with multiple strategies
- **Position management** for both LONG and SHORT positions

## 📞 Support

For questions or issues:
- **GitHub Issues**: [IronBeam API Issues](https://github.com/ENHarry/IronBeam_api/issues)
- **IronBeam API Docs**: [Official API Documentation](https://docs.ironbeamapi.com/)

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.