import re
from collections import defaultdict

def analyze_responses(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    analysis = {
        'total_questions': 0,
        'answered': 0,
        'no_info': 0,
        'sections': defaultdict(lambda: {'total': 0, 'answered': 0, 'no_info': 0}),
        'sources': defaultdict(int),
        'common_gaps': [],
        'i_dont_responses': []  # New section for "I don't" responses
    }

    sections = re.split(r'={80,}', content)
    current_section = None

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split('\n')
        if len(lines) > 1:
            current_section = lines[0].strip()
            
            # Find Q&A pairs
            for i in range(len(lines)):
                if '📝 Question:' in lines[i]:
                    question = lines[i].replace('📝 Question:', '').strip()
                    # Find corresponding answer
                    for j in range(i, min(i+5, len(lines))):
                        if '🔍 Answer:' in lines[j]:
                            answer = lines[j].replace('🔍 Answer:', '').strip()
                            analysis['total_questions'] += 1
                            analysis['sections'][current_section]['total'] += 1

                            # Check for "I don't" responses
                            if answer.lower().startswith("i don't") or "don't have" in answer.lower():
                                analysis['no_info'] += 1
                                analysis['sections'][current_section]['no_info'] += 1
                                analysis['i_dont_responses'].append({
                                    'section': current_section,
                                    'question': question,
                                    'answer': answer
                                })
                            else:
                                analysis['answered'] += 1
                                analysis['sections'][current_section]['answered'] += 1

                            # Get source
                            for k in range(j, min(j+3, len(lines))):
                                if '📚 Source Document:' in lines[k]:
                                    source = lines[k].replace('📚 Source Document:', '').replace('•', '').strip()
                                    analysis['sources'][source] += 1
                                    break
                            break

    return analysis

def print_analysis_report(analysis):
    print("\n=== Security Questionnaire Analysis Report ===\n")
    
    # Overall Statistics
    print("📊 Overall Statistics:")
    print(f"Total Questions: {analysis['total_questions']}")
    print(f"Answered Questions: {analysis['answered']} ({(analysis['answered']/analysis['total_questions']*100):.1f}%)")
    print(f"Questions Lacking Information: {analysis['no_info']} ({(analysis['no_info']/analysis['total_questions']*100):.1f}%)")
    
    # Section Analysis
    print("\n📑 Section-wise Analysis:")
    for section, stats in analysis['sections'].items():
        if section and not section.isspace():
            print(f"\n{section}:")
            total = stats['total']
            if total > 0:
                print(f"  - Total Questions: {total}")
                print(f"  - Answered: {stats['answered']} ({(stats['answered']/total*100):.1f}%)")
                print(f"  - No Information: {stats['no_info']} ({(stats['no_info']/total*100):.1f}%)")

    # Source Documents
    print("\n📚 Source Documents Usage:")
    for source, count in sorted(analysis['sources'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {source}: {count} references")

    # "I don't" Responses
    print("\n❌ Questions with 'I don't have' or similar responses:")
    for i, response in enumerate(analysis['i_dont_responses'], 1):
        print(f"\n{i}. Section: {response['section']}")
        print(f"   Question: {response['question']}")
        print(f"   Response: {response['answer']}")

    # Recommendations
    print("\n💡 Recommendations:")
    if analysis['no_info']/analysis['total_questions'] > 0.3:
        print("  - High number of unanswered questions. Consider gathering more documentation.")
    
    sections_needing_attention = [
        section for section, stats in analysis['sections'].items()
        if stats['no_info']/stats['total'] > 0.5
    ]
    if sections_needing_attention:
        print("  - Sections needing immediate attention:")
        for section in sections_needing_attention:
            print(f"    * {section}")

    # Priority Areas
    print("\n🎯 Priority Areas for Documentation:")
    section_priorities = sorted(
        [(s, stats['no_info']/stats['total']) 
         for s, stats in analysis['sections'].items()],
        key=lambda x: x[1],
        reverse=True
    )
    for section, ratio in section_priorities[:3]:
        print(f"  - {section}: {ratio*100:.1f}% missing information")

if __name__ == "__main__":
    file_path = "security_questionnaire_responses_2024-10-28 20-39-36.txt"
    analysis = analyze_responses(file_path)
    print_analysis_report(analysis)
