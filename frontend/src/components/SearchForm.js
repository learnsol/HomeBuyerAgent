import React from 'react';
import { Form, Input, InputNumber, Button, Card, Row, Col, Space, Tag, Select } from 'antd';
import { SearchOutlined, DollarOutlined, HomeOutlined, HeartOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;

const SearchForm = ({ onSearch }) => {
  const [form] = Form.useForm();

  const handleSubmit = (values) => {
    // Transform form values to match backend expected format
    const searchData = {
      search_criteria: {
        price_max: values.price_max,
        price_min: values.price_min,
        bedrooms_min: values.bedrooms_min || 1,
        bathrooms_min: values.bathrooms_min || 1,
        keywords: values.keywords ? values.keywords.split(',').map(k => k.trim()) : []
      },
      user_financial_info: {
        annual_income: values.annual_income,
        down_payment_percentage: values.down_payment_percentage || 20,
        monthly_debts: values.monthly_debts || 0
      },
      priorities: values.priorities || []
    };
    
    onSearch(searchData);
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{
        price_max: 750000,
        price_min: 300000,
        bedrooms_min: 3,
        bathrooms_min: 2,
        annual_income: 120000,
        down_payment_percentage: 20,
        monthly_debts: 800
      }}
    >
      <Card 
        title={<span><HomeOutlined style={{ marginRight: 8 }} />Property Preferences</span>}
        style={{ marginBottom: 16 }}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              label="Maximum Price"
              name="price_max"
              rules={[{ required: true, message: 'Please enter maximum price' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={value => value.replace(/\$\s?|(,*)/g, '')}
                min={0}
                placeholder="750,000"
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              label="Minimum Price"
              name="price_min"
              rules={[{ required: true, message: 'Please enter minimum price' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={value => value.replace(/\$\s?|(,*)/g, '')}
                min={0}
                placeholder="300,000"
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Form.Item label="Min Bedrooms" name="bedrooms_min">
              <InputNumber style={{ width: '100%' }} min={1} max={10} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Form.Item label="Min Bathrooms" name="bathrooms_min">
              <InputNumber style={{ width: '100%' }} min={1} max={10} step={0.5} />
            </Form.Item>
          </Col>
        </Row>
          <Form.Item label="Property Features & Amenities (comma-separated)" name="keywords">
          <TextArea 
            rows={2} 
            placeholder="Enter specific features you want: modern kitchen, large backyard, pool, garage, fireplace, hardwood floors"
          />
        </Form.Item>
      </Card>

      <Card 
        title={<span><DollarOutlined style={{ marginRight: 8 }} />Financial Information</span>}
        style={{ marginBottom: 16 }}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              label="Annual Income"
              name="annual_income"
              rules={[{ required: true, message: 'Please enter your annual income' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={value => value.replace(/\$\s?|(,*)/g, '')}
                min={0}
                placeholder="120,000"
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item label="Down Payment %" name="down_payment_percentage">
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                max={100}
                formatter={value => `${value}%`}
                parser={value => value.replace('%', '')}
                placeholder="20"
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item label="Monthly Debts" name="monthly_debts">
              <InputNumber
                style={{ width: '100%' }}
                formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={value => value.replace(/\$\s?|(,*)/g, '')}
                min={0}
                placeholder="800"
              />
            </Form.Item>
          </Col>
        </Row>
      </Card>      <Card 
        title={<span><HeartOutlined style={{ marginRight: 8 }} />What Matters Most to You?</span>}
        style={{ marginBottom: 24 }}
      >
        <div style={{ marginBottom: 12, color: '#666', fontSize: '14px' }}>
          <strong>Note:</strong> This is different from property features above. Select your life priorities that will guide our AI recommendations.
        </div>
        <Form.Item label="Your Personal Priorities (select multiple)" name="priorities">
          <Select
            mode="multiple"
            placeholder="What aspects of homeownership are most important to your lifestyle?"
            style={{ width: '100%' }}
          >
            <Option value="good school district">Good School District</Option>
            <Option value="safety">Safety & Low Crime</Option>
            <Option value="affordability">Affordability</Option>
            <Option value="large backyard">Large Backyard</Option>
            <Option value="modern kitchen">Modern Kitchen</Option>
            <Option value="close to work">Close to Work</Option>
            <Option value="walkable neighborhood">Walkable Neighborhood</Option>
            <Option value="low maintenance">Low Maintenance</Option>
            <Option value="investment potential">Investment Potential</Option>
            <Option value="quiet area">Quiet Area</Option>
          </Select>
        </Form.Item>
      </Card>

      <div style={{ textAlign: 'center' }}>
        <Button 
          type="primary" 
          htmlType="submit" 
          size="large"
          icon={<SearchOutlined />}
          style={{ 
            minWidth: '200px',
            height: '48px',
            fontSize: '16px',
            fontWeight: '600'
          }}
        >
          Find My Perfect Home
        </Button>
      </div>
    </Form>
  );
};

export default SearchForm;
