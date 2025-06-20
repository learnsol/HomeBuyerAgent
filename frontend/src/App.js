import React, { useState } from 'react';
import { Layout, Typography, Card, Space, Spin } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import SearchForm from './components/SearchForm';
import ProgressTracker from './components/ProgressTracker';
import RecommendationResults from './components/RecommendationResults';
import { analyzeHomeBuyingRequest } from './services/api';
import './index.css';

const { Header, Content } = Layout;
const { Title, Paragraph } = Typography;

function App() {
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (searchData) => {
    setLoading(true);
    setCurrentStep(0);
    setResults(null);
    setError(null);

    try {
      // Simulate step progression
      const steps = [
        'Searching for properties...',
        'Analyzing localities...',
        'Evaluating safety & hazards...',
        'Calculating affordability...',
        'Generating recommendations...'
      ];

      // Start the analysis
      const resultPromise = analyzeHomeBuyingRequest(searchData);
      
      // Simulate progress updates
      for (let i = 0; i < steps.length; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay per step
      }

      const result = await resultPromise;
      setResults(result);
      setCurrentStep(steps.length);
    } catch (err) {
      setError(err.message || 'An error occurred while processing your request');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = () => {
    setResults(null);
    setError(null);
    setCurrentStep(0);
  };

  return (
    <Layout style={{ minHeight: '100vh', padding: '0' }}>      <Header style={{ 
        background: 'rgba(255, 255, 255, 0.15)', 
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        padding: '0 24px',
        textAlign: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <HomeOutlined style={{ fontSize: '32px', color: 'white', marginRight: '16px' }} />
          <Title level={1} style={{ 
            margin: 0, 
            color: 'white',
            fontSize: '2.5rem',
            fontWeight: 'bold',
            textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
            background: 'linear-gradient(45deg, #ffffff, #f0f8ff)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            🏠 AI Home Buyer Assistant
          </Title>
        </div>
      </Header>
      
      <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {!results && !loading && (
            <Card className="home-search-container" style={{ padding: '24px' }}>
              <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <Title level={2}>Find Your Perfect Home</Title>
                <Paragraph style={{ fontSize: '16px', color: '#666' }}>
                  Our AI-powered assistant analyzes properties, neighborhoods, safety factors, 
                  and affordability to provide personalized home recommendations.
                </Paragraph>
              </div>
              <SearchForm onSearch={handleSearch} />
            </Card>
          )}

          {loading && (
            <Card className="progress-container" style={{ padding: '24px' }}>
              <ProgressTracker currentStep={currentStep} />
            </Card>
          )}

          {error && (
            <Card style={{ background: '#fff2f0', border: '1px solid #ffccc7' }}>
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <Title level={4} style={{ color: '#cf1322', margin: 0 }}>
                  Error Processing Request
                </Title>
                <Paragraph style={{ color: '#cf1322', marginTop: '8px' }}>
                  {error}
                </Paragraph>
              </div>
            </Card>
          )}

          {results && (
            <RecommendationResults 
              results={results} 
              onNewSearch={handleNewSearch}
            />
          )}
        </Space>
      </Content>
    </Layout>
  );
}

export default App;
