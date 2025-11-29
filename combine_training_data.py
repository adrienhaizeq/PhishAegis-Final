import pandas as pd
import glob
import os

def combine_all_training_data():
    """Combine all training datasets into one master file"""
    
    # Find all CSV files
    csv_files = glob.glob('*training*.csv') + glob.glob('*dataset*.csv') + ['enron_legit.csv']
    
    all_dataframes = []
    
    for file in csv_files:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file)
                # Standardize column names
                if 'email_text' in df.columns:
                    df = df.rename(columns={'email_text': 'body'})
                
                # Ensure we have required columns
                if 'subject' in df.columns and 'body' in df.columns and 'label' in df.columns:
                    all_dataframes.append(df)
                    print(f"✅ Loaded: {file} ({len(df)} emails)")
                else:
                    print(f"⚠️  Skipped {file} - missing required columns")
                    
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")
        else:
            print(f"📝 Not found: {file}")
    
    if all_dataframes:
        # Combine all data
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Remove duplicates based on subject and body
        combined_df = combined_df.drop_duplicates(subset=['subject', 'body'])
        
        # Clean labels
        combined_df['label'] = combined_df['label'].str.lower().replace({
            'legit': 'legitimate',
            'ham': 'legitimate', 
            'spam': 'phishing',
            'malicious': 'phishing'
        })
        
        # Save combined dataset
        combined_df.to_csv('master_training_dataset.csv', index=False)
        
        print(f"\n🎉 COMBINED DATASET CREATED!")
        print(f"📊 Total emails: {len(combined_df)}")
        print(f"🔒 Legitimate: {len(combined_df[combined_df['label'] == 'legitimate'])}")
        print(f"🚨 Phishing: {len(combined_df[combined_df['label'] == 'phishing'])}")
        print(f"📁 File: master_training_dataset.csv")
        
        return combined_df
    else:
        print("❌ No training files found!")
        return None

if __name__ == '__main__':
    combine_all_training_data()