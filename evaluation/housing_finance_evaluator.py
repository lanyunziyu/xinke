#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购房资金方案自动评测系统

用于验证购房资金方案生成的准确性，包括：
1. 首付计算准确性
2. 贷款和月供计算准确性
3. 税费计算准确性
4. 政策适用性判断
5. 资金方案完整性

使用方法：
    python housing_finance_evaluator.py
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from loguru import logger
import difflib

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.housing_finance_agent import HousingFinanceAgent
from tools.trading_knowledge_retriever_tool import TradingKnowledgeRetrieverTool
from tools.quark_web_search_tool import QuarkWebSearchTool
from tools.trade_cost_calculate_tool import TradeCostCalculateTool
from tools.trade_cost_calculate_form_tool import TradeCostCalculateFormTool
from tools.report_generator import ReportGeneratorTool


class HousingFinanceEvaluator:
    """购房资金方案自动评测器"""

    def __init__(self, testcases_file: str):
        """
        初始化评测器

        Args:
            testcases_file: 测试用例JSON文件路径
        """
        self.testcases_file = Path(testcases_file)
        self.testcases = self._load_testcases()

        # 初始化Agent
        self.agent = self._initialize_agent()

        # 评测结果
        self.results = []

        logger.info(f"评测器初始化完成，加载了 {len(self.testcases)} 个测试用例")

    def _load_testcases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        logger.info(f"加载测试用例: {self.testcases_file}")

        with open(self.testcases_file, 'r', encoding='utf-8') as f:
            testcases = json.load(f)

        logger.info(f"成功加载 {len(testcases)} 个测试用例")
        return testcases

    def _initialize_agent(self) -> HousingFinanceAgent:
        """初始化购房资金Agent"""
        logger.info("初始化购房资金Agent...")

        tools = {
            "trading_knowledge_retriever": TradingKnowledgeRetrieverTool(),
            "quark_web_search": QuarkWebSearchTool(),
            "trade_cost_calculate": TradeCostCalculateTool(),
            "trade_cost_calculate_form": TradeCostCalculateFormTool(),
            "report_generator": ReportGeneratorTool()
        }

        agent = HousingFinanceAgent(tools=tools)
        logger.info("Agent初始化完成")

        return agent

    def run_evaluation(self) -> Dict[str, Any]:
        """
        运行完整评测

        Returns:
            评测结果汇总
        """
        logger.info("=" * 80)
        logger.info("开始运行购房资金方案评测")
        logger.info("=" * 80)

        start_time = datetime.now()

        for i, testcase in enumerate(self.testcases, 1):
            logger.info(f"\n{'=' * 80}")
            logger.info(f"测试用例 {i}/{len(self.testcases)}: {testcase['name']}")
            logger.info(f"ID: {testcase['test_id']}")
            logger.info(f"描述: {testcase['description']}")
            logger.info(f"{'=' * 80}")

            result = self._evaluate_single_case(testcase)
            self.results.append(result)

            logger.info(f"\n测试结果: {'✓ 通过' if result['passed'] else '✗ 失败'}")
            logger.info(f"得分: {result['score']:.1f}%")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 生成评测报告
        summary = self._generate_summary(duration)

        logger.info("\n" + "=" * 80)
        logger.info("评测完成")
        logger.info("=" * 80)

        return summary

    def _evaluate_single_case(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """
        评测单个测试用例

        Args:
            testcase: 测试用例

        Returns:
            评测结果
        """
        test_id = testcase['test_id']
        user_query = testcase['input']['user_query']
        expected = testcase['expected_output']
        validation_points = testcase.get('validation_points', [])

        logger.info(f"\n用户查询: {user_query}")

        # 运行Agent
        try:
            agent_result = self.agent.run(user_query, max_iterations=15)

            if agent_result['status'] != 'success':
                return {
                    'test_id': test_id,
                    'name': testcase['name'],
                    'passed': False,
                    'score': 0.0,
                    'error': agent_result.get('error', 'Agent执行失败'),
                    'details': []
                }

            response = agent_result['response']
            logger.info(f"\nAgent响应预览:\n{response[:500]}...")

        except Exception as e:
            logger.error(f"Agent执行异常: {e}")
            return {
                'test_id': test_id,
                'name': testcase['name'],
                'passed': False,
                'score': 0.0,
                'error': str(e),
                'details': []
            }

        # 执行验证点检查
        validation_results = []
        total_points = len(validation_points)
        passed_points = 0

        for vp in validation_points:
            validation_result = self._validate_point(vp, response, expected)
            validation_results.append(validation_result)

            if validation_result['passed']:
                passed_points += 1

        # 计算得分
        score = (passed_points / total_points * 100) if total_points > 0 else 0
        passed = score >= 80.0  # 80分及格

        return {
            'test_id': test_id,
            'name': testcase['name'],
            'passed': passed,
            'score': score,
            'total_points': total_points,
            'passed_points': passed_points,
            'validation_results': validation_results,
            'agent_response': response,
            'iterations': agent_result.get('iterations', 0)
        }

    def _validate_point(
        self,
        validation_point: Dict[str, Any],
        response: str,
        expected: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        验证单个验证点

        Args:
            validation_point: 验证点配置
            response: Agent响应
            expected: 期望输出

        Returns:
            验证结果
        """
        key = validation_point['key']
        description = validation_point['description']
        validation_type = validation_point['validation_type']

        logger.info(f"\n验证: {description}")

        try:
            if validation_type == 'exact_match':
                result = self._validate_exact_match(key, response, expected, validation_point)
            elif validation_type == 'range':
                result = self._validate_range(key, response, expected, validation_point)
            elif validation_type == 'boolean':
                result = self._validate_boolean(key, response, expected, validation_point)
            elif validation_type == 'percentage':
                result = self._validate_percentage(key, response, expected, validation_point)
            elif validation_type == 'keyword_match':
                result = self._validate_keyword_match(key, response, expected, validation_point)
            elif validation_type == 'exists':
                result = self._validate_exists(key, response, expected, validation_point)
            elif validation_type == 'structure':
                result = self._validate_structure(key, response, expected, validation_point)
            elif validation_type == 'string_match':
                result = self._validate_string_match(key, response, expected, validation_point)
            else:
                result = {
                    'passed': False,
                    'message': f"未知的验证类型: {validation_type}"
                }

            logger.info(f"结果: {'✓ 通过' if result['passed'] else '✗ 失败'} - {result['message']}")

            return {
                'key': key,
                'description': description,
                'validation_type': validation_type,
                **result
            }

        except Exception as e:
            logger.error(f"验证异常: {e}")
            return {
                'key': key,
                'description': description,
                'validation_type': validation_type,
                'passed': False,
                'message': f"验证异常: {str(e)}"
            }

    def _validate_exact_match(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """精确匹配验证"""
        # 从response中提取数值
        if key == 'down_payment':
            # 提取首付金额
            pattern = r'首付.*?(\d+(?:\.\d+)?)\s*万'
            match = re.search(pattern, response)
            if match:
                actual_value = float(match.group(1)) * 10000
                expected_value = expected['down_payment']['amount']

                if abs(actual_value - expected_value) < 10000:  # 允许1万元误差
                    return {
                        'passed': True,
                        'message': f"首付金额匹配: {actual_value/10000}万元",
                        'actual': actual_value,
                        'expected': expected_value
                    }
                else:
                    return {
                        'passed': False,
                        'message': f"首付金额不匹配: 实际{actual_value/10000}万，期望{expected_value/10000}万",
                        'actual': actual_value,
                        'expected': expected_value
                    }
            else:
                return {
                    'passed': False,
                    'message': "未能从响应中提取首付金额"
                }

        elif key == 'loan_amount':
            # 提取贷款金额
            pattern = r'贷款.*?(\d+(?:\.\d+)?)\s*万'
            match = re.search(pattern, response)
            if match:
                actual_value = float(match.group(1)) * 10000
                expected_value = expected['loan']['amount']

                if abs(actual_value - expected_value) < 10000:
                    return {
                        'passed': True,
                        'message': f"贷款金额匹配: {actual_value/10000}万元",
                        'actual': actual_value,
                        'expected': expected_value
                    }
                else:
                    return {
                        'passed': False,
                        'message': f"贷款金额不匹配: 实际{actual_value/10000}万，期望{expected_value/10000}万",
                        'actual': actual_value,
                        'expected': expected_value
                    }
            else:
                return {
                    'passed': False,
                    'message': "未能从响应中提取贷款金额"
                }

        elif key == 'deed_tax_rate':
            # 提取契税率
            pattern = r'契税.*?(\d+(?:\.\d+)?)\s*%'
            match = re.search(pattern, response)
            if match:
                actual_value = float(match.group(1)) / 100
                expected_value = expected['taxes']['deed_tax']['rate']

                if abs(actual_value - expected_value) < 0.001:
                    return {
                        'passed': True,
                        'message': f"契税率匹配: {actual_value*100}%",
                        'actual': actual_value,
                        'expected': expected_value
                    }
                else:
                    return {
                        'passed': False,
                        'message': f"契税率不匹配: 实际{actual_value*100}%，期望{expected_value*100}%",
                        'actual': actual_value,
                        'expected': expected_value
                    }
            else:
                return {
                    'passed': False,
                    'message': "未能从响应中提取契税率"
                }

        else:
            return {
                'passed': False,
                'message': f"未实现的验证key: {key}"
            }

    def _validate_range(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """范围验证"""
        if key == 'monthly_payment':
            # 提取月供金额
            pattern = r'月供.*?(\d+(?:\.\d+)?)\s*万|月供.*?(\d+)\s*元'
            match = re.search(pattern, response)

            if match:
                if match.group(1):
                    actual_value = float(match.group(1)) * 10000
                else:
                    actual_value = float(match.group(2))

                expected_range = expected['loan']['monthly_payment_range']
                min_val = expected_range['min']
                max_val = expected_range['max']

                if min_val <= actual_value <= max_val:
                    return {
                        'passed': True,
                        'message': f"月供在合理范围内: {actual_value}元 (范围: {min_val}-{max_val}元)",
                        'actual': actual_value,
                        'expected_range': [min_val, max_val]
                    }
                else:
                    return {
                        'passed': False,
                        'message': f"月供超出范围: 实际{actual_value}元，期望{min_val}-{max_val}元",
                        'actual': actual_value,
                        'expected_range': [min_val, max_val]
                    }
            else:
                # 尝试从报告中查找
                if '月供' in response or '还款' in response:
                    return {
                        'passed': True,
                        'message': "响应中包含月供信息（无法精确提取数值）"
                    }
                else:
                    return {
                        'passed': False,
                        'message': "未能从响应中提取月供金额"
                    }

        return {
            'passed': False,
            'message': f"未实现的范围验证key: {key}"
        }

    def _validate_boolean(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """布尔验证"""
        if key == 'tax_exemptions':
            # 检查满五唯一免税
            exempt_keywords = ['免征', '免', '不需要缴纳', '无需缴纳']
            personal_tax_exempt = any(
                keyword in response and '个税' in response[max(0, response.find(keyword)-20):response.find(keyword)+30]
                for keyword in exempt_keywords
            )

            vat_exempt = any(
                keyword in response and ('增值税' in response[max(0, response.find(keyword)-20):response.find(keyword)+30] or
                                        '营业税' in response[max(0, response.find(keyword)-20):response.find(keyword)+30])
                for keyword in exempt_keywords
            )

            if personal_tax_exempt and vat_exempt:
                return {
                    'passed': True,
                    'message': "正确识别满五唯一免征个税和增值税"
                }
            else:
                return {
                    'passed': False,
                    'message': f"税费豁免识别不完整: 个税{'免征' if personal_tax_exempt else '未识别'}, 增值税{'免征' if vat_exempt else '未识别'}"
                }

        elif key == 'eligibility_check':
            expected_value = vp.get('expected_value', True)

            # 检查资格判断
            if expected_value is False:
                # 期望不符合资格
                negative_keywords = ['不符合', '不满足', '无法', '不能', '需要', '还需']
                is_negative = any(keyword in response for keyword in negative_keywords)

                if is_negative:
                    return {
                        'passed': True,
                        'message': "正确判断不符合购房资格"
                    }
                else:
                    return {
                        'passed': False,
                        'message': "未能正确判断购房资格限制"
                    }
            else:
                positive_keywords = ['符合', '满足', '可以', '能够']
                is_positive = any(keyword in response for keyword in positive_keywords)

                if is_positive:
                    return {
                        'passed': True,
                        'message': "正确判断符合购房资格"
                    }
                else:
                    return {
                        'passed': False,
                        'message': "未能正确判断购房资格"
                    }

        elif key == 'personal_income_tax':
            # 检查个税是否需要缴纳
            expected_applicable = expected['taxes']['personal_income_tax'].get('applicable', False)
            exempt = expected['taxes']['personal_income_tax'].get('exempt', False)

            if exempt:
                # 期望免征
                exempt_keywords = ['免征', '免', '不需要缴纳']
                is_exempt = any(
                    keyword in response and '个税' in response[max(0, response.find(keyword)-20):response.find(keyword)+30]
                    for keyword in exempt_keywords
                )

                if is_exempt:
                    return {
                        'passed': True,
                        'message': "正确识别个税免征"
                    }
                else:
                    return {
                        'passed': False,
                        'message': "未能识别个税免征"
                    }
            elif expected_applicable:
                # 期望需要缴纳
                applicable_keywords = ['需要缴纳', '应缴纳', '个税', '个人所得税']
                is_applicable = any(keyword in response for keyword in applicable_keywords)

                if is_applicable:
                    return {
                        'passed': True,
                        'message': "正确识别需要缴纳个税"
                    }
                else:
                    return {
                        'passed': False,
                        'message': "未能识别需要缴纳个税"
                    }

        elif key == 'tax_liability':
            # 检查不满两年的税费义务
            vat_keywords = ['增值税', '营业税']
            personal_tax_keywords = ['个税', '个人所得税']

            has_vat = any(keyword in response for keyword in vat_keywords)
            has_personal_tax = any(keyword in response for keyword in personal_tax_keywords)

            if has_vat and has_personal_tax:
                return {
                    'passed': True,
                    'message': "正确识别不满两年需缴纳增值税和个税"
                }
            else:
                return {
                    'passed': False,
                    'message': f"税费义务识别不完整: {'增值税' if has_vat else '未提及增值税'}, {'个税' if has_personal_tax else '未提及个税'}"
                }

        return {
            'passed': False,
            'message': f"未实现的布尔验证key: {key}"
        }

    def _validate_percentage(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """百分比验证"""
        if key == 'down_payment_ratio':
            expected_value = vp.get('expected_value', 0.3)

            # 提取首付比例
            pattern = r'首付.*?(\d+)\s*%'
            match = re.search(pattern, response)

            if match:
                actual_value = float(match.group(1)) / 100

                if abs(actual_value - expected_value) < 0.01:
                    return {
                        'passed': True,
                        'message': f"首付比例匹配: {actual_value*100}%",
                        'actual': actual_value,
                        'expected': expected_value
                    }
                else:
                    return {
                        'passed': False,
                        'message': f"首付比例不匹配: 实际{actual_value*100}%，期望{expected_value*100}%",
                        'actual': actual_value,
                        'expected': expected_value
                    }
            else:
                return {
                    'passed': False,
                    'message': "未能从响应中提取首付比例"
                }

        return {
            'passed': False,
            'message': f"未实现的百分比验证key: {key}"
        }

    def _validate_keyword_match(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """关键词匹配验证"""
        keywords = vp.get('keywords', [])

        matched_keywords = [kw for kw in keywords if kw in response]

        if len(matched_keywords) >= len(keywords) * 0.7:  # 70%关键词匹配即可
            return {
                'passed': True,
                'message': f"关键词匹配成功: {matched_keywords}",
                'matched_keywords': matched_keywords
            }
        else:
            return {
                'passed': False,
                'message': f"关键词匹配不足: 匹配{len(matched_keywords)}/{len(keywords)}个",
                'matched_keywords': matched_keywords,
                'missing_keywords': [kw for kw in keywords if kw not in matched_keywords]
            }

    def _validate_exists(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """存在性验证"""
        if key == 'alternative_provided':
            # 检查是否提供了替代建议
            suggestion_keywords = ['建议', '可以', '考虑', '方案', '选择']

            has_suggestions = any(keyword in response for keyword in suggestion_keywords)

            if has_suggestions:
                return {
                    'passed': True,
                    'message': "提供了替代建议"
                }
            else:
                return {
                    'passed': False,
                    'message': "未提供替代建议"
                }

        return {
            'passed': False,
            'message': f"未实现的存在性验证key: {key}"
        }

    def _validate_structure(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """结构验证"""
        if key == 'loan_structure':
            # 检查组合贷结构
            has_commercial = '商贷' in response or '商业贷款' in response
            has_provident = '公积金' in response or '公积金贷款' in response

            if has_commercial and has_provident:
                return {
                    'passed': True,
                    'message': "正确识别组合贷结构（商贷+公积金）"
                }
            else:
                return {
                    'passed': False,
                    'message': f"组合贷结构不完整: {'商贷' if has_commercial else '缺少商贷'}, {'公积金' if has_provident else '缺少公积金'}"
                }

        return {
            'passed': False,
            'message': f"未实现的结构验证key: {key}"
        }

    def _validate_string_match(self, key: str, response: str, expected: Dict, vp: Dict) -> Dict:
        """字符串匹配验证"""
        if key == 'repayment_method':
            # 检查还款方式
            if '等额本金' in response:
                return {
                    'passed': True,
                    'message': "正确识别等额本金还款方式"
                }
            elif '等额本息' in response:
                return {
                    'passed': False,
                    'message': "还款方式识别错误: 应为等额本金，实际为等额本息"
                }
            else:
                return {
                    'passed': False,
                    'message': "未能识别还款方式"
                }

        return {
            'passed': False,
            'message': f"未实现的字符串匹配验证key: {key}"
        }

    def _generate_summary(self, duration: float) -> Dict[str, Any]:
        """
        生成评测摘要

        Args:
            duration: 评测耗时（秒）

        Returns:
            评测摘要
        """
        total_cases = len(self.results)
        passed_cases = sum(1 for r in self.results if r['passed'])
        failed_cases = total_cases - passed_cases

        total_points = sum(r['total_points'] for r in self.results)
        passed_points = sum(r['passed_points'] for r in self.results)

        average_score = sum(r['score'] for r in self.results) / total_cases if total_cases > 0 else 0

        summary = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'total_cases': total_cases,
            'passed_cases': passed_cases,
            'failed_cases': failed_cases,
            'pass_rate': passed_cases / total_cases * 100 if total_cases > 0 else 0,
            'total_validation_points': total_points,
            'passed_validation_points': passed_points,
            'validation_pass_rate': passed_points / total_points * 100 if total_points > 0 else 0,
            'average_score': average_score,
            'results': self.results
        }

        return summary

    def save_report(self, summary: Dict[str, Any], output_file: str):
        """
        保存评测报告

        Args:
            summary: 评测摘要
            output_file: 输出文件路径
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"评测报告已保存: {output_path}")

    def print_summary(self, summary: Dict[str, Any]):
        """打印评测摘要"""
        print("\n" + "=" * 80)
        print("购房资金方案评测报告")
        print("=" * 80)
        print(f"评测时间: {summary['timestamp']}")
        print(f"评测耗时: {summary['duration_seconds']:.2f}秒")
        print()
        print(f"测试用例总数: {summary['total_cases']}")
        print(f"通过用例: {summary['passed_cases']} ({summary['pass_rate']:.1f}%)")
        print(f"失败用例: {summary['failed_cases']}")
        print()
        print(f"验证点总数: {summary['total_validation_points']}")
        print(f"通过验证点: {summary['passed_validation_points']} ({summary['validation_pass_rate']:.1f}%)")
        print(f"平均得分: {summary['average_score']:.1f}分")
        print()
        print("=" * 80)
        print("详细结果:")
        print("=" * 80)

        for result in summary['results']:
            status = "✓" if result['passed'] else "✗"
            print(f"\n{status} [{result['test_id']}] {result['name']}")
            print(f"  得分: {result['score']:.1f}% ({result['passed_points']}/{result['total_points']})")

            if 'error' in result:
                print(f"  错误: {result['error']}")

            if not result['passed']:
                print(f"  失败的验证点:")
                for vr in result.get('validation_results', []):
                    if not vr['passed']:
                        print(f"    - {vr['description']}: {vr['message']}")

        print("\n" + "=" * 80)

        # 总结
        if summary['pass_rate'] >= 80:
            print("🎉 评测通过！购房资金方案准确性良好。")
        elif summary['pass_rate'] >= 60:
            print("⚠️  评测部分通过，仍有改进空间。")
        else:
            print("❌ 评测未通过，需要重点改进。")

        print("=" * 80)


def main():
    """主函数"""
    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # 评测文件路径
    testcases_file = Path(__file__).parent / "housing_finance_testcases.json"
    report_file = Path(__file__).parent / "reports" / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # 创建评测器
    evaluator = HousingFinanceEvaluator(testcases_file)

    # 运行评测
    summary = evaluator.run_evaluation()

    # 保存报告
    evaluator.save_report(summary, report_file)

    # 打印摘要
    evaluator.print_summary(summary)

    # 返回退出码
    sys.exit(0 if summary['pass_rate'] >= 80 else 1)


if __name__ == "__main__":
    main()
