import React from 'react';
import { Card, Steps, Typography, Space, Spin } from 'antd';
import { 
  SearchOutlined, 
  EnvironmentOutlined, 
  SafetyOutlined, 
  DollarOutlined, 
  StarOutlined,
  LoadingOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Step } = Steps;

const steps = [
  {
    title: 'Finding Properties',
    description: 'Searching for homes that match your criteria...',
    icon: <SearchOutlined />
  },
  {
    title: 'Analyzing Locations',
    description: 'Evaluating neighborhoods and local amenities...',
    icon: <EnvironmentOutlined />
  },
  {
    title: 'Safety Assessment',
    description: 'Checking hazards, crime rates, and safety factors...',
    icon: <SafetyOutlined />
  },
  {
    title: 'Financial Analysis',
    description: 'Calculating affordability and investment potential...',
    icon: <DollarOutlined />
  },
  {
    title: 'Creating Recommendations',
    description: 'Generating personalized home recommendations...',
    icon: <StarOutlined />
  }
];

const ProgressTracker = ({ currentStep }) => {
  return (
    <Card style={{ textAlign: 'center' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Spin 
            indicator={<LoadingOutlined style={{ fontSize: 48, color: '#1890ff' }} spin />} 
          />
          <Title level={3} style={{ marginTop: 16, marginBottom: 8 }}>
            Analyzing Your Home Search
          </Title>
          <Text type="secondary" style={{ fontSize: '16px' }}>
            Our AI agents are working together to find the perfect homes for you
          </Text>
        </div>

        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <Steps 
            current={currentStep} 
            direction="vertical" 
            size="small"
            style={{ textAlign: 'left' }}
          >
            {steps.map((step, index) => (
              <Step
                key={index}
                title={step.title}
                description={step.description}
                icon={index === currentStep ? <LoadingOutlined spin /> : step.icon}
                status={
                  index < currentStep ? 'finish' : 
                  index === currentStep ? 'process' : 'wait'
                }
              />
            ))}
          </Steps>
        </div>

        <div className="step-details" style={{ marginTop: '24px' }}>
          {currentStep < steps.length && (
            <Card size="small" style={{ background: '#f8f9fa', border: 'none' }}>
              <Text strong style={{ color: '#1890ff' }}>
                Currently: {steps[currentStep]?.title}
              </Text>
              <br />
              <Text type="secondary">
                {steps[currentStep]?.description}
              </Text>
            </Card>
          )}
        </div>
      </Space>
    </Card>
  );
};

export default ProgressTracker;
