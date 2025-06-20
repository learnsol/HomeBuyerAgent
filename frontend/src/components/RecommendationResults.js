import React from 'react';
import { Card, Typography, Button, Row, Col, Tag, Space, Divider, Progress } from 'antd';
import { 
  HomeOutlined, 
  DollarOutlined, 
  EnvironmentOutlined, 
  SafetyOutlined,
  StarOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

const RecommendationResults = ({ results, onNewSearch }) => {
  if (!results || !results.top_recommendations) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <WarningOutlined style={{ fontSize: '48px', color: '#faad14' }} />
          <Title level={3} style={{ marginTop: '16px' }}>
            No Results Found
          </Title>
          <Paragraph>
            We couldn't find any properties matching your criteria. 
            Try adjusting your search parameters.
          </Paragraph>
          <Button type="primary" onClick={onNewSearch}>
            Try New Search
          </Button>
        </div>
      </Card>
    );
  }

  const { top_recommendations, summary } = results;

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* Summary Card */}
      <Card className="recommendation-card">
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
          <Title level={2} style={{ marginTop: '16px', marginBottom: '8px' }}>
            Your Home Recommendations Are Ready!
          </Title>
          <Text type="secondary" style={{ fontSize: '16px' }}>
            We analyzed {summary?.total_listings || top_recommendations.length} properties 
            and found {top_recommendations.length} perfect matches for you.
          </Text>
        </div>
        
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <Button 
            type="default" 
            icon={<ReloadOutlined />} 
            onClick={onNewSearch}
            size="large"
          >
            Start New Search
          </Button>
        </div>
      </Card>

      {/* Recommendations List */}
      {top_recommendations.map((property, index) => (
        <Card 
          key={property.listing_id || index}
          className="recommendation-card"
          title={
            <Space>
              <StarOutlined style={{ color: '#faad14' }} />
              <span>Recommendation #{index + 1}</span>
              <Tag color="blue">Score: {property.total_score || 'N/A'}</Tag>
            </Space>
          }
        >
          <Row gutter={[24, 24]}>
            {/* Property Details */}
            <Col xs={24} lg={12}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Title level={4} style={{ marginBottom: '8px' }}>
                    <HomeOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                    {property.address || 'Property Address'}
                  </Title>
                  <Space wrap>
                    <Tag icon={<DollarOutlined />} color="green">
                      ${property.price?.toLocaleString() || 'N/A'}
                    </Tag>
                    <Tag>{property.bedrooms || 'N/A'} bed</Tag>
                    <Tag>{property.bathrooms || 'N/A'} bath</Tag>
                    {property.square_footage && (
                      <Tag>{property.square_footage?.toLocaleString()} sq ft</Tag>
                    )}
                  </Space>
                </div>

                {/* Property Description */}
                {property.description && (
                  <div>
                    <Text strong>Description:</Text>
                    <br />
                    <Text type="secondary">{property.description}</Text>
                  </div>
                )}

                {/* Pros and Cons */}
                <div>
                  {property.pros && property.pros.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <Text strong style={{ color: '#52c41a' }}>✅ Highlights:</Text>
                      <div style={{ marginTop: '4px' }}>
                        {property.pros.slice(0, 4).map((pro, idx) => (
                          <Tag key={idx} color="green" style={{ margin: '2px' }}>
                            {pro}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  )}

                  {property.cons && property.cons.length > 0 && (
                    <div>
                      <Text strong style={{ color: '#fa8c16' }}>⚠️ Considerations:</Text>
                      <div style={{ marginTop: '4px' }}>
                        {property.cons.slice(0, 3).map((con, idx) => (
                          <Tag key={idx} color="orange" style={{ margin: '2px' }}>
                            {con}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </Space>
            </Col>

            {/* Analysis Scores */}
            <Col xs={24} lg={12}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Title level={5}>Analysis Breakdown</Title>
                
                {/* Affordability Score */}
                {property.affordability_score !== undefined && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span><DollarOutlined /> Affordability</span>
                      <span>{property.affordability_score}/25</span>
                    </div>
                    <Progress 
                      percent={(property.affordability_score / 25) * 100} 
                      size="small"
                      strokeColor="#52c41a"
                      showInfo={false}
                    />
                  </div>
                )}

                {/* Locality Score */}
                {property.locality_score !== undefined && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span><EnvironmentOutlined /> Location</span>
                      <span>{property.locality_score}/25</span>
                    </div>
                    <Progress 
                      percent={(property.locality_score / 25) * 100} 
                      size="small"
                      strokeColor="#1890ff"
                      showInfo={false}
                    />
                  </div>
                )}

                {/* Safety Score */}
                {property.safety_score !== undefined && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span><SafetyOutlined /> Safety</span>
                      <span>{property.safety_score}/25</span>
                    </div>
                    <Progress 
                      percent={(property.safety_score / 25) * 100} 
                      size="small"
                      strokeColor="#fa8c16"
                      showInfo={false}
                    />
                  </div>
                )}

                {/* Overall Score */}
                <Divider style={{ margin: '12px 0' }} />
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span><StarOutlined /> Overall Score</span>
                    <span style={{ fontWeight: 'bold' }}>{property.total_score || 'N/A'}/100</span>
                  </div>
                  <Progress 
                    percent={property.total_score || 0} 
                    size="small"
                    strokeColor="#722ed1"
                    showInfo={false}
                  />
                </div>

                {/* Recommendation Summary */}
                {property.recommendation_summary && (
                  <div style={{ 
                    background: '#f6ffed', 
                    border: '1px solid #b7eb8f',
                    borderRadius: '6px',
                    padding: '12px',
                    marginTop: '12px'
                  }}>
                    <Text strong style={{ color: '#389e0d' }}>AI Recommendation:</Text>
                    <br />
                    <Text style={{ fontSize: '14px' }}>{property.recommendation_summary}</Text>
                  </div>
                )}
              </Space>
            </Col>
          </Row>
        </Card>
      ))}
    </Space>
  );
};

export default RecommendationResults;
