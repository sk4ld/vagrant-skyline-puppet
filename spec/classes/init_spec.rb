require 'spec_helper'
describe 'skyline' do

  context 'with defaults for all parameters' do
    it { should contain_class('skyline') }
  end
end
